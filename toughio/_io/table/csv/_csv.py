import numpy as np

from ...._common import open_file

__all__ = [
    "read",
]


def read(filename):
    """
    Read CSV table file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.

    Returns
    -------
    dict
        Table data.

    Note
    ----
    Also supports iTOUGH2 .foft files.

    """
    with open_file(filename, "r") as f:
        line = f.readline().strip()

        if line.startswith('"'):
            sep = ","
            line = line.replace('"', "")

        else:
            sep = None

        headers = [x.strip() for x in line.split(sep)]

        data = []
        line = f.readline().strip()
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

        return out
