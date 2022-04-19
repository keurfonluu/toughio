from __future__ import with_statement

from functools import partial

import numpy as np

from ...._common import get_label_length, open_file
from ..._common import read_record
from .._common import to_output

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order, label_length=None):
    """Read standard TOUGH OUTPUT."""
    with open_file(filename, "r") as f:
        headers, times, variables = _read_table(f, file_type, label_length)

        ilab = 1 if file_type == "element" else 2
        headers = headers[ilab + 1 :]
        labels = [[v[:ilab] for v in variable] for variable in variables]
        labels = (
            [[l[0] for l in label] for label in labels]
            if file_type == "element"
            else labels
        )
        variables = np.array(
            [[v[ilab + 1 :] for v in variable] for variable in variables]
        )

    return to_output(
        file_type, file_format, labels_order, headers, times, labels, variables
    )


def _read_table(f, file_type, label_length):
    """Read data table for current time step."""
    labels_key = "ELEM." if file_type == "element" else "ELEM1"

    first = True
    times, variables = [], []
    for line in f:
        line = line.strip()

        # Look for "TOTAL TIME"
        if line.startswith("TOTAL TIME"):
            # Read time step in following line
            line = next(f).strip()
            times.append(float(line.split()[0]))
            variables.append([])

            # Look for "ELEM." or "ELEM1"
            while True:
                try:
                    line = next(f).strip()
                    if line.startswith(labels_key):
                        break

                except StopIteration:
                    raise ValueError("No data related to {}s found.".format(file_type))

            # Read headers
            headers = line.split()

            # Look for next non-empty line
            while True:
                line = next(f)
                if line.strip():
                    break

            # Loop until end of output block
            while True:
                if line[:10].strip() and not line.strip().startswith("ELEM"):
                    line = line.lstrip()

                    if first and not label_length:
                        label_length = get_label_length(line[:9])
                        iend = (
                            label_length
                            if file_type == "element"
                            else 2 * label_length + 2
                        )

                    tmp = (
                        [line[:label_length]]
                        if file_type == "element"
                        else [line[:label_length], line[label_length + 2 : iend]]
                    )

                    line = line[iend:]
                    if first:
                        try:
                            # Set line parser and try parsing first line
                            reader = lambda line: [to_float(x) for x in line.split()]
                            _ = reader(line)

                        except ValueError:
                            # Determine number of characters for index
                            idx = line.replace("-", " ").split()[0]
                            nidx = line.index(idx) + len(idx)
                            ifmt = "{}s".format(nidx)

                            # Determine number of characters between two Es
                            i1 = line.find("E")
                            i2 = line.find("E", i1 + 1)

                            # Initialize data format
                            fmt = [ifmt]
                            if i2 >= 0:
                                di = i2 - i1
                                dfmt = "{}.{}e".format(di, di - 7)
                                fmt += 20 * [dfmt]  # Read 20 data columns at most
                            else:
                                fmt += ["12.5e"]
                            fmt = ",".join(fmt)

                            # Set line parser
                            reader = partial(read_record, fmt=fmt)

                        finally:
                            first = False

                    tmp += reader(line)
                    variables[-1].append([x for x in tmp if x is not None])

                line = next(f)
                if line[1:].startswith("@@@@@"):
                    break

    return headers, times, variables


def to_float(x):
    """Return np.nan if x cannot be converted."""
    from ..._common import to_float as _to_float

    try:
        return _to_float(x)

    except ValueError:
        return np.nan
