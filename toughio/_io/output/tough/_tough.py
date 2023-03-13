from functools import partial

import numpy as np

from ...._common import open_file
from ..._common import read_record
from .._common import to_output

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order):
    """Read standard TOUGH OUTPUT."""
    with open_file(filename, "r") as f:
        headers, times, variables = _read_table(f, file_type)

        # Postprocess labels
        labels = [v[0].lstrip() for v in variables[0]]

        if file_type == "element":
            label_length = max(len(label) for label in labels)
            fmt = f"{{:>{label_length}}}"
            labels = [fmt.format(label) for label in labels]

        else:
            # Find end of first element processing backward
            labels = [label[::-1] for label in labels]
            tmp = max(labels, key=len)

            while True:
                iend = tmp.index(" ")

                if iend < 2:
                    tmp = f"{tmp[:iend]}0{tmp[iend + 1:]}"

                else:
                    break

            iend += len(tmp[iend:]) - len(tmp[iend:].lstrip())

            # Split connection names
            labels1 = [label[iend:].rstrip() for label in labels]
            labels2 = [label[:iend].rstrip() for label in labels]

            # Find label length
            len1 = max(len(label) for label in labels1)
            len2 = max(len(label) for label in labels2)
            label_length = max(len1, len2)

            # Correct element names given label length
            fmt = f"{{:<{label_length}}}"
            labels1 = [fmt.format(label) for label in labels1]
            labels2 = [fmt.format(label) for label in labels2]
            labels = [[l1[::-1], l2[::-1]] for l1, l2 in zip(labels1, labels2)]

        ilab = 1 if file_type == "element" else 2
        headers = headers[ilab + 1 :]
        labels = [labels.copy() for _ in variables]
        variables = np.array([[v[2:] for v in variable] for variable in variables])

    return to_output(
        file_type, file_format, labels_order, headers, times, labels, variables
    )


def _read_table(f, file_type):
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
                    raise ValueError(f"No data related to {file_type}s found.")

            # Read headers
            headers = line.split()

            # Look for next non-empty line
            while True:
                line = next(f)
                if line.strip():
                    break

            # Loop until end of output block
            while True:
                if line[:15].strip() and not line.strip().startswith("ELEM"):
                    if first:
                        # Find first floating point
                        for xf in line.split()[::-1]:
                            try:
                                _ = int(xf)

                            except ValueError:
                                x = xf
                                continue

                            break

                        # Find end of label(s)
                        tmp = line[: line.index(x)].rstrip()
                        tmp = tmp[::-1]
                        tmp = tmp[: line.index(" ") : -1].rstrip()
                        iend = len(tmp)

                    tmp = [line[:iend]]
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
                            ifmt = f"{nidx}s"

                            # Determine number of characters between two Es
                            i1 = line.find("E")
                            i2 = line.find("E", i1 + 1)

                            # Initialize data format
                            fmt = [ifmt]
                            if i2 >= 0:
                                di = i2 - i1
                                dfmt = f"{di}.{di - 7}e"
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
