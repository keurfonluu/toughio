from __future__ import annotations

import os
from typing import TextIO

import pandas as pd

from .output.tecplot._tecplot import read_buffer
from ..core import WellOutput
from .._common import open_file


def read(filename: str | os.PathLike | TextIO) -> WellOutput:
    """
    Read TECPLOT well output file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Well output file name or buffer.

    Returns
    -------
    :class:`toughio.WellOutput`
        Well output data.

    """
    with open_file(filename, "r") as f:
        headers, zones = read_buffer(f)

    data = [list(row) for row in zip(*zones[0]["data"])]
    df = pd.DataFrame({k: v for k, v in zip(headers, data)})
    out = []

    for well_id, well_df in df.groupby("WellID"):
        out.append(WellOutput(well_df.sort_values(["Time", "Depth"]).to_dict(orient="list")))
    
    return out
