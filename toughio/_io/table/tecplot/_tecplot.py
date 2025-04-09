from __future__ import annotations

import os
from typing import TextIO

import numpy as np

from .._common import to_output
from ...output.tecplot._tecplot import read_buffer
from ...._common import open_file


def read(filename: str | os.PathLike | TextIO) -> HistoryOutput:
    """
    Read TECPLOT table file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        History file name or buffer.

    Returns
    -------
    :class:`toughio.HistoryOutput`
        History output data.

    """
    with open_file(filename, "r") as f:
        headers, zones = read_buffer(f)

    out = {headers[0]: zones[0]["data"][:, 0]}
    for zone in zones:
        out[zone["title"]] = zone["data"][:, 1]

    return to_output(out, filename)
