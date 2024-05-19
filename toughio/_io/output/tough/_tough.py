from functools import partial

import numpy as np

from ...._common import open_file
from ..._common import read_record, to_float
from .._common import to_output

__all__ = [
    "read",
]


def read(filename, file_type, labels_order=None, time_steps=None):
    """
    Read standard TOUGH output file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_type : str
        Input file type.
    labels_order : sequence of array_like
        List of labels. If None, output will be assumed ordered.
    time_steps : int or sequence of int
        List of time steps to read. If None, all time steps will be read.

    Returns
    -------
    :class:`toughio.ElementOutput`, :class:`toughio.ConnectionOutput`, sequence of :class:`toughio.ElementOutput` or sequence of :class:`toughio.ConnectionOutput`
        Output data for each time step.

    """
    if time_steps is not None:
        if isinstance(time_steps, int):
            time_steps = [time_steps]

        if any(i < 0 for i in time_steps):
            n_steps = _count_time_steps(filename)
            time_steps = [i if i >= 0 else n_steps + i for i in time_steps]

        time_steps = set(time_steps)

    with open_file(filename, "r") as f:
        headers, times, data = _read_table(f, file_type, time_steps)

        # Postprocess labels
        labels = [v[0].lstrip() for v in data[0]]

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
        labels = [labels.copy() for _ in data]
        data = np.array([[v[2:] for v in data] for data in data])

    return to_output(file_type, labels_order, headers, times, labels, data)


def _read_table(f, file_type, time_steps=None):
    """Read data table for current time step."""
    labels_key = "ELEM." if file_type == "element" else "ELEM1"

    t_step = -1
    times, data = [], []
    for line in f:
        line = line.strip()

        # Look for "TOTAL TIME"
        if line.startswith("TOTAL TIME"):
            t_step += 1

            if time_steps is not None and t_step > max(time_steps):
                break

            if not (time_steps is None or t_step in time_steps):
                continue

            # Read time step in following line
            line = next(f).strip()
            times.append(float(line.split()[0]))
            data.append([])

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

            # Read units
            line = next(f)
            nwsp = line.index(
                line.strip()[0]
            )  # Index of first non whitespace character

            # Look for next non-empty line
            while True:
                line = next(f)
                if line.strip():
                    break

            # Loop until end of output block
            reader = lambda line: [to_float(x) for x in line.split()]
            reader2 = None

            while True:
                if line[:nwsp].strip() and not line.strip().startswith("ELEM"):
                    if reader2 is None:
                        # Find first floating point
                        x = line.split()[-headers[::-1].index("INDEX")]

                        # Find end of label(s)
                        tmp = line[: line.index(x)].rstrip()
                        tmp = tmp[::-1]
                        tmp = tmp[: line.index(" ") : -1].rstrip()
                        iend = len(tmp)

                    tmp = [line[:iend]]
                    line = line[iend:]

                    if reader2 is None:
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

                        # Set second line parser
                        reader2 = partial(read_record, fmt=fmt)

                    try:
                        tmp += reader(line)

                    except ValueError:
                        tmp += reader2(line)

                    data[-1].append([x for x in tmp if x is not None])

                line = next(f)
                if line[1:].startswith("@@@@@"):
                    break

    return headers, times, data


def _count_time_steps(filename):
    """Count the number of time steps."""
    with open_file(filename, "r") as f:
        count = 0

        for line in f:
            count += int(line.strip().startswith("TOTAL TIME"))

    return count
