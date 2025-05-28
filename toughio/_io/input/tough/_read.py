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
        else [block.name for block, _ in registered_blocks]
    )
    blocks = set(blocks)

    with open_file(filename, "r") as f:
        out = read_buffer(f, blocks, label_length, n_variables, free_format, eos, simulator)

    return out


def read_buffer(
    f: TextIO,
    block_stack: Sequence[str] = None,
    label_length: Optional[int] = None,
    n_variables: Optional[int] = None,
    free_format: bool = False,
    eos: Optional[str] = None,
    simulator: Literal["tough", "tough3", "tough4", "toughreact"] = "tough",
):
    """Read TOUGH input file."""
    block_readers = {
        block.name: block(free_format=free_format)
        for block, _ in registered_blocks
    }

    if simulator != "tough4":
        block_readers["TIMBC"].free_format = True
        block_readers["TIMBC"].delimiter = None

    # Read blocks
    parameters = {}
    flag = False

    # Title
    if "TITLE" in block_stack:
        block_stack.remove("TITLE")
        title = block_readers["TITLE"].read(f)
        parameters["title"] = title

    # Loop over blocks
    # Some blocks (INCON, INDOM, PARAM) need to rewind to previous line but tell and seek are disabled by next
    # See <https://stackoverflow.com/questions/22688505/is-there-a-way-to-go-back-when-reading-a-file-using-seek-and-calls-to-next>
    fiter = FileIterator(f)

    try:
        for line in fiter:
            if line.startswith("DIMEN") and "DIMEN" in block_stack:
                block_stack.remove("DIMEN")
                dimen = block_readers["DIMEN"].read(fiter)
                parameters.update(dimen)

            elif line.startswith("ROCKS") and "ROCKS" in block_stack:
                block_stack.remove("ROCKS")
                rocks = block_readers["ROCKS"].read(fiter, simulator=simulator)
                parameters.update(rocks)

            elif line.startswith("RPCAP") and "RPCAP" in block_stack:
                block_stack.remove("RPCAP")
                rpcap = block_readers["RPCAP"].read(fiter)
                parameters.setdefault("default", {}).update(rpcap)

            elif line.startswith("REACT") and "REACT" in block_stack:
                block_stack.remove("REACT")
                react = block_readers["REACT"].read(fiter)
                parameters.setdefault("react", {}).update(react["react"])

            elif line.startswith("FLAC") and "FLAC" in block_stack:
                block_stack.remove("FLAC")
                flac = block_readers["FLAC"].read(fiter, parameters["rocks"])
                parameters["flac"] = flac["flac"]

            elif line.startswith("CHEMP") and "CHEMP" in block_stack:
                block_stack.remove("CHEMP")
                chemp = block_readers["CHEMP"].read(fiter)
                parameters.update(chemp)

            elif line.startswith("NCGAS") and "NCGAS" in block_stack:
                block_stack.remove("NCGAS")
                ncgas = block_readers["NCGAS"].read(fiter)
                parameters.update(ncgas)

            elif line.startswith("MULTI") and "MULTI" in block_stack:
                block_stack.remove("MULTI")
                multi = block_readers["MULTI"].read(fiter)
                parameters.update(multi)

                if not n_variables:
                    n_variables = parameters["n_component"] + 1

            elif line.startswith("SOLVR") and "SOLVR" in block_stack:
                block_stack.remove("SOLVR")
                solvr = block_readers["SOLVR"].read(fiter)
                parameters.update(solvr)

            elif line.startswith("INDEX") and "INDEX" in block_stack:
                block_stack.remove("INDEX")
                parameters["index"] = True

            elif line.startswith("START") and "START" in block_stack:
                block_stack.remove("START")
                parameters["start"] = True

            elif line.startswith("PARAM") and "PARAM" in block_stack:
                block_stack.remove("PARAM")
                param = block_readers["PARAM"].read(
                    fiter, n_variables, eos,
                )
                n_variables = param["n_variables"]
                parameters["options"] = param["data"]["options"]
                parameters["extra_options"] = param["data"]["extra_options"]
                parameters.setdefault("default", {}).update(param["data"]["default"])

            elif line.startswith("SELEC") and "SELEC" in block_stack:
                block_stack.remove("SELEC")
                selec = block_readers["SELEC"].read(fiter)
                parameters.update(selec)

            elif line.startswith("INDOM") and "INDOM" in block_stack:
                block_stack.remove("INDOM")
                indom = block_readers["INDOM"].read(
                    fiter, n_variables, eos,
                )
                n_variables = indom["n_variables"]

                for k, v in indom["data"]["rocks"].items():
                    parameters["rocks"][k].update(v)

            elif line.startswith("MOMOP") and "MOMOP" in block_stack:
                block_stack.remove("MOMOP")
                momop = block_readers["MOMOP"].read(fiter)
                parameters.update(momop)

            elif line.startswith("TIMES") and "TIMES" in block_stack:
                block_stack.remove("TIMES")
                times = block_readers["TIMES"].read(fiter)
                parameters.update(times)

            elif line.startswith("HYSTE") and "HYSTE" in block_stack:
                block_stack.remove("HYSTE")
                hyste = block_readers["HYSTE"].read(fiter)
                parameters.update(hyste)

            elif line.startswith("FOFT") and "FOFT" in block_stack:
                block_stack.remove("FOFT")
                foft = block_readers["FOFT"].read(fiter, label_length)
                parameters.update(foft["data"])
                label_length = foft["label_length"]

            elif line.startswith("COFT") and "COFT" in block_stack:
                block_stack.remove("COFT")
                coft = block_readers["COFT"].read(fiter, label_length)
                parameters.update(coft["data"])
                label_length = coft["label_length"]

            elif line.startswith("GOFT") and "GOFT" in block_stack:
                block_stack.remove("GOFT")
                goft = block_readers["GOFT"].read(fiter, label_length)
                parameters.update(goft["data"])
                label_length = goft["label_length"]

            elif line.startswith("ROFT") and "ROFT" in block_stack:
                block_stack.remove("ROFT")
                roft = block_readers["ROFT"].read(fiter)
                parameters.update(roft)

            elif line.startswith("GENER") and "GENER" in block_stack:
                block_stack.remove("GENER")
                gener = block_readers["GENER"].read(
                    fiter, label_length, simulator,
                )
                parameters.update(gener["data"])
                label_length = gener["label_length"]
                flag = gener["flag"]

                if flag:
                    break

            elif line.startswith("TIMBC") and "TIMBC" in block_stack:
                block_stack.remove("TIMBC")
                timbc = block_readers["TIMBC"].read(fiter, simulator)
                parameters.update(timbc)

            elif line.startswith("DIFFU") and "DIFFU" in block_stack:
                block_stack.remove("DIFFU")
                diffu = block_readers["DIFFU"].read(fiter)
                parameters.update(diffu)

            elif line.startswith("OUTPT") and "OUTPT" in block_stack:
                block_stack.remove("OUTPT")
                outpt = block_readers["OUTPT"].read(fiter)
                parameters.setdefault("react", {}).update(outpt["react"])

            elif line.startswith("OUTPU") and "OUTPU" in block_stack:
                block_stack.remove("OUTPU")
                outpu = block_readers["OUTPU"].read(fiter)
                parameters.update(outpu)

            elif line.startswith("ELEME") and "ELEME" in block_stack:
                block_stack.remove("ELEME")
                eleme = block_readers["ELEME"].read(fiter, label_length)
                parameters.update(eleme["data"])
                label_length = eleme["label_length"]

                parameters["coordinates"] = False

            elif line.startswith("COORD") and "COORD" in block_stack:
                block_stack.remove("COORD")
                coord = block_readers["COORD"].read(fiter)

                for k, v in zip(parameters["elements"], coord):
                    parameters["elements"][k]["center"] = v

                parameters["coordinates"] = True

            elif line.startswith("CONNE") and "CONNE" in block_stack:
                block_stack.remove("CONNE")
                conne = block_readers["CONNE"].read(
                    fiter, label_length,
                )
                parameters.update(conne["data"])
                label_length = conne["label_length"]
                flag = conne["flag"]

                if flag:
                    break

            elif line.startswith("INCON") and "INCON" in block_stack:
                block_stack.remove("INCON")
                incon = block_readers["INCON"].read(
                    fiter, label_length, n_variables, eos, simulator,
                )
                parameters.update(incon["data"])
                label_length = incon["label_length"]
                n_variables = incon["n_variables"]
                flag = incon["flag"]

                if flag:
                    break

            elif line.startswith("MESHM") and "MESHM" in block_stack:
                block_stack.remove("MESHM")
                meshm = block_readers["MESHM"].read(fiter)
                parameters.update(meshm)

            elif line.startswith("POISE") and "POISE" in block_stack:
                block_stack.remove("POISE")
                poise = block_readers["POISE"].read(fiter)
                parameters.setdefault("react", {}).update(poise["react"])

            elif line.startswith("NOVER") and "NOVER" in block_stack:
                block_stack.remove("NOVER")
                parameters["nover"] = True

            elif line.startswith("ENDCY") and "ENDCY" in block_stack:
                block_stack.remove("ENDCY")
                end_comments = block_readers["END COMMENTS"].read(fiter)

                if end_comments:
                    parameters["end_comments"] = end_comments

            # Stop reading if block stack is empty
            if not block_stack:
                break

    except:
        raise ReadError(f"failed to parse line {fiter.count}.")

    if flag:
        end_comments = block_readers["END COMMENTS"].read(fiter)

        if end_comments:
            if isinstance(end_comments, str):
                end_comments = [end_comments]

            parameters["end_comments"] = ["+++", *end_comments]

    return parameters
