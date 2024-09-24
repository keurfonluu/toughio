from __future__ import annotations
from typing import TextIO

import os

import numpy as np

from .._common import to_output
from ...._common import open_file


def read(filename: str | os.PathLike | TextIO) -> HistoryOutput:
    """
    Read CSV table file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        History file name or buffer.

    Returns
    -------
    :class:`toughio.HistoryOutput`
        History output data.

    Note
    ----
    Also supports iTOUGH2 .foft files.

    """
    with open_file(filename, "r") as f:
        # Read headers
        line = f.readline().strip()
        sep = "," if "," in line else None

        headers = []
        while True:
            hdr = [x.replace('"', "").strip() for x in line.split(sep)]

            try:
                _ = float(hdr[0])
                break

            except ValueError:
                headers.append(hdr)
                line = f.readline().strip()

        headers = [" ".join(hdr) for hdr in zip(*headers)]

        # Read data
        data = []
        while line:
            data.append([x.replace('"', "").strip() for x in line.split(sep)])
            line = f.readline().strip()

        out = {}
        for header, X in zip(headers, np.transpose(data)):
            # Remove extra whitespaces
            header = " ".join(header.split())

            if header in {"KCYC", "ROCK"}:
                out[header] = np.array([int(x) for x in X])

            elif header.startswith("ELEM"):
                label_length = max(len(x) for x in X)
                fmt = f"{{:>{label_length}}}"
                out[header] = np.array([fmt.format(x) for x in X])

            else:
                out[header] = np.array([float(x) for x in X])

    return to_output(out, filename)
