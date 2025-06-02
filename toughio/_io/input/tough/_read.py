from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Literal, Optional, TextIO

from ...._common import open_file
from ....core import FileIterator, ReadError
from .blocks import registered_blocks


def read(
    filename: str | os.PathLike | TextIO,
    blocks: Optional[Sequence[str]] = None,
    label_length: Optional[int] = None,
    n_variables: Optional[int] = None,
    free_format: bool = False,
    eos: Optional[str] = None,
    simulator: Literal["tough", "tough3", "tough4", "toughreact"] = "tough",
) -> dict:
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Input file name or buffer.
    blocks : Sequence[str], optional
        Blocks to read. If None, read all blocks.
    label_length : int, optional
        Number of characters in cell labels.
    n_variables : int, optional
        Number of primary variables.
    free_format : bool, default False
        If True, assume records are comma-separated.
    simulator : str {'tough', 'tough3', 'tough4', 'toughreact'}, default 'tough'
        Simulator type.
    eos : str, optional
        Equation of State. Ignored if *eos* is defined in *parameters*.

    Returns
    -------
    dict
        TOUGH input parameters.

    """
    if not (label_length is None or isinstance(label_length, int)):
        raise TypeError()

    if isinstance(label_length, int) and not 5 <= label_length < 10:
        raise ValueError()

    if simulator not in {"tough", "tough3", "tough4", "toughreact"}:
        raise ValueError()

    blocks = (
        blocks
        if blocks is not None
        else [block.name for block in registered_blocks]
    )
    blocks = tuple(blocks)

    with open_file(filename, "r") as f:
        out = read_buffer(f, blocks, label_length, n_variables, free_format, eos, simulator)

    return out


def read_buffer(
    f: TextIO,
    blocks: Sequence[str] = None,
    label_length: Optional[int] = None,
    n_variables: Optional[int] = None,
    free_format: bool = False,
    eos: Optional[str] = None,
    simulator: Literal["tough", "tough3", "tough4", "toughreact"] = "tough",
):
    """Read TOUGH input file."""
    block_readers = {
        block.name: block(free_format=free_format)
        for block in registered_blocks
    }

    if simulator != "tough4":
        block_readers["TIMBC"].free_format = True
        block_readers["TIMBC"].delimiter = None

    # Read blocks
    parameters = {}
    flag = False

    # Title
    if "TITLE" in blocks:
        blocks = tuple(block for block in blocks if block != "TITLE")
        title = block_readers["TITLE"].read(f)
        block_readers["TITLE"].update(parameters, title)

    # Loop over blocks
    # Some blocks (INCON, INDOM, PARAM) need to rewind to previous line but tell and seek are disabled by next
    # See <https://stackoverflow.com/questions/22688505/is-there-a-way-to-go-back-when-reading-a-file-using-seek-and-calls-to-next>
    fiter = FileIterator(f)

    try:
        for line in fiter:
            if line.startswith(blocks):
                name = line[:5].rstrip().upper()
                blocks = tuple(block for block in blocks if block != name)
                data = block_readers[name].read(
                    fiter,
                    parameters=parameters,
                    label_length=label_length,
                    n_variables=n_variables,
                    eos=eos,
                    simulator=simulator,
                )
                block_readers[name].update(parameters, data)

                if not label_length and "label_length" in data:
                    label_length = data["label_length"]

                if not n_variables and "n_variables" in data:
                    n_variables = data["n_variables"]

                if "flag" in data:
                    flag = data["flag"]

                if flag or not blocks or name == "ENDCY":
                    break

    except:
        raise ReadError(f"failed to parse line {fiter.count}.")

    end_comments = block_readers["END COMMENTS"].read(fiter)

    if flag:
        end_comments["end_comments"].insert(0, "+++")

    block_readers["END COMMENTS"].update(parameters, end_comments)

    return parameters
