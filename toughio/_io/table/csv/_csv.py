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

        return out
