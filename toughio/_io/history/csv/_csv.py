import numpy as np

from ...._common import open_file

__all__ = [
    "read",
]


def read(filename):
    """
    Read CSV history file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.

    Returns
    -------
    dict
        History data.

    """
    with open_file(filename, "r") as f:
        line = f.readline().strip()

        if line.startswith('"'):
            sep = ","
            line = line.replace('"', "")
        else:
            sep = None
        headers = [x.strip() for x in line.split(sep)[1:]]

        data = []
        line = f.readline().strip()
        while line:
            data += [[float(x) for x in line.split(sep)]]
            line = f.readline().strip()
        data = np.transpose(data)

        out = {"TIME": data[0]}
        for header, X in zip(headers, data[1:]):
            out[header] = X

        return out
