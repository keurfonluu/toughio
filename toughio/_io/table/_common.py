from __future__ import annotations
from typing import TextIO

import io
import os
import pathlib

from ...core import HistoryOutput


def to_output(
    output: dict,
    filename: str | os.PathLike,
) -> HistoryOutput:
    """
    Create history output with label.

    Parameters
    ----------
    output : dict
        History output as a dict.
    filename : str | PathLike | TextIO
        History output file name or buffer.

    Returns
    -------
    :class:`toughio.HistoryOutput`
        History output data.

    """
    output = HistoryOutput(output)
    
    # Extract label
    if isinstance(filename, io.TextIOWrapper):
        try:
            filename = filename.name

        except AttributeError:
            filename = ""

    filename = pathlib.Path(filename).stem
    label = filename[5:]

    if filename.upper().startswith("FOFT_"):
        output.label = label
        output.type = "element"

    elif filename.upper().startswith("GOFT_"):
        name = label[-5:].strip("_")
        label = label[:-6]
        output.label = f"{label}-{name}"
        output.type = "generator"

    elif filename.upper().startswith(("COFT_", "ROFT_")):
        label_length = len(label) // 2
        l1, l2 = label[:label_length], label[label_length + 1:]
        output.label = f"{l1.strip('_')}-{l2.strip('_')}"
        output.type = "connection" if filename.upper().startswith("COFT") else "rock"

    return output
