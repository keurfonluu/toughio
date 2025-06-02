from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Literal, Optional, TextIO

from .blocks import registered_blocks
from ...._common import open_file


def write(
    filename: str | os.PathLike | TextIO,
    parameters: dict,
    blocks: Optional[Sequence[str]] = None,
    space_between_blocks: bool = False,
    space_between_values: bool = False,
    free_format: bool = False,
    eos: Optional[str] = None,
    simulator: Literal["tough", "tough3", "tough4", "toughreact"] = "tough",
    block: Optional[Literal["all", "gener", "mesh", "incon"] | Sequence[str]] = None,
    ignore_blocks: Optional[Sequence[str]] = None,
) -> None:
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Output file name or buffer.
    parameters : dict
        Parameters to export.
    blocks : Sequence[str], optional
        Blocks to write.
    space_between_blocks : bool, default False
        If True, add an empty record between blocks.
    space_between_values : bool, default False
        If True, add a white space between floating point values.
    free_format : bool, default False
        If True, write comma-separated free-format records.
    simulator : str {'tough', 'tough3', 'tough4', 'toughreact'}, default 'tough'
        Simulator type.
    eos : str, optional
        Equation of State. Ignored if *eos* is defined in *parameters*.
    block : {'all', 'gener', 'mesh', 'incon'}, optional
        Blocks to write:

         - 'all': write all blocks
         - 'gener': only write block GENER
         - 'mesh': only write blocks ELEME, COORD and CONNE
         - 'incon': only write block INCON
         - None: write all blocks except blocks defined in *ignore_blocks*.
        
        Ignored if *blocks* is not None.

    ignore_blocks : Sequence[str], optional
        Blocks to ignore. Only if *blocks* is not None and if *block* is None.

    Note
    ----
    The option *blocks* is the preferred way to specify which blocks to write. The
    options *block* and *ignore_blocks* parameters are only kept for backward
    compatibility and may be removed in future versions.

    """
    if simulator not in {"tough", "tough3", "tough4", "toughreact"}:
        raise ValueError(f"invalid simulator '{simulator}'")

    if blocks is None:
        blocks = [block.name for block in registered_blocks]

        if block is not None:
            if block.lower() == "all":
                blocks = set(blocks)

            elif block.lower() == "gener":
                blocks = {"GENER", "END COMMENTS"}

            elif block.lower() == "mesh":
                blocks = {"ELEME", "COORD", "CONNE", "END COMMENTS"}

            elif block.lower() == "incon":
                blocks = {"INCON", "END COMMENTS"}

            else:
                raise ValueError()

        elif ignore_blocks is not None:
            blocks = set([block for block in blocks if block not in ignore_blocks])
            
    else:
        blocks = set(blocks)

    buffer = write_buffer(
        parameters,
        blocks,
        space_between_blocks,
        space_between_values,
        free_format,
        parameters.get("eos", eos),
        simulator,
    )

    with open_file(filename, "w") as f:
        for record in buffer:
            f.write(record)


def write_buffer(
    parameters: dict,
    blocks: Sequence[str],
    space_between_blocks: bool = False,
    space_between_values: bool = True,
    free_format: bool = False,
    eos: Optional[str] = None,
    simulator: Literal["tough", "toughreact"] = "tough",	
) -> list[str]:
    """Write TOUGH input file as a list of 80-character long record strings."""
    block_writers = {
        block.name: block(
            space_between_values=space_between_values,
            space_between_blocks=space_between_blocks,
            free_format=free_format,
        )
        for block in registered_blocks
        if block.name in blocks
    }

    if "TIMBC" in blocks and simulator != "tough4":
        block_writers["TIMBC"].free_format = True
        block_writers["TIMBC"].space_between_values = True
        block_writers["TIMBC"].delimiter = ""

    # Write blocks
    out = []

    for block in block_writers.values():
        out += block.write(parameters, eos=eos, simulator=simulator)

    return out
