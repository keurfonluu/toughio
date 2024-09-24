from __future__ import annotations
from typing import TextIO

import os

import numpy as np

from .._common import to_output
from ...._common import open_file


def read(filename: str | os.PathLike | TextIO) -> HistoryOutput:
    """
    Read COLUMN table file.

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
        line1 = f.readline().rstrip()
        line2 = f.readline().rstrip()

        # Find the number of columns
        line3 = f.readline().rstrip()
        tmp = line3

        ncol = 0
        ncols = [0]
        while tmp.strip():
            ncol = len(tmp) - len(tmp.lstrip())
            ncol += len(tmp.split()[0])
            tmp = tmp[ncol:]
            ncols.append(ncol)

        icols = np.cumsum(ncols)

        # Gather data
        data = [[float(x) for x in line3.split()]]

        for line in f:
            data += [[float(x) for x in line.split()]]

        data = np.transpose(data)

        # Parse headers
        headers = []
        for i1, i2 in zip(icols[:-1], icols[1:]):
            h1 = line1[i1:i2].strip()
            h2 = line2[i1:i2].strip()
            headers.append(f"{h1} {h2}")

        out = {k: v for k, v in zip(headers, data)}

    return to_output(out, filename)
