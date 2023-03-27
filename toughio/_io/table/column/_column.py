import numpy as np

from ...._common import open_file

__all__ = [
    "read",
]


def read(filename):
    """
    Read COLUMN table file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.

    Returns
    -------
    dict
        Table data.

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

        return {k: v for k, v in zip(headers, data)}
