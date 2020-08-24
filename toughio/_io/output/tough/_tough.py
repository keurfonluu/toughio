from __future__ import with_statement

import numpy

from ...._common import get_label_length
from ...input.tough._helpers import read_record
from .._common import to_output

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order, label_length=None):
    """Read standard TOUGH OUTPUT."""
    with open(filename, "r") as f:
        headers, times, variables = _read_table(f, file_type, label_length)

        ilab = 1 if file_type == "element" else 2
        headers = headers[ilab + 1 :]
        labels = [[v[:ilab] for v in variable] for variable in variables]
        labels = (
            [[l[0] for l in label] for label in labels]
            if file_type == "element"
            else labels
        )
        variables = numpy.array(
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
    while True:
        line = f.readline().strip()

        # Look for "TOTAL TIME"
        if line.startswith("TOTAL TIME"):
            # Read time step in following line
            line = f.readline().strip()
            times.append(float(line.split()[0]))
            variables.append([])

            # Look for "ELEM." or "ELEM1"
            while True:
                line = f.readline().strip()
                if line.startswith(labels_key):
                    break
                elif _end_of_file(line):
                    raise ValueError("No data related to {}s found.".format(file_type))

            # Read headers
            headers = line.split()

            # Look for next non-empty line
            while True:
                line = f.readline()
                if line.strip():
                    break

            # Loop until end of output block
            while True:
                if line[:10].strip() and not line.strip().startswith("ELEM"):
                    line = line.lstrip()

                    if first and not label_length:
                        label_length = get_label_length(line[:9])
                        iend = (
                            label_length if file_type == "element" else 2 * label_length + 2
                        )
                        
                    tmp = (
                        [line[:label_length]]
                        if file_type == "element"
                        else [line[:label_length], line[label_length + 2 : iend]]
                    )

                    line = line[iend:]
                    if first:
                        # Determine number of characters for index
                        idx = line.replace("-", " ").split()[0]
                        nidx = line.index(idx) + len(idx)
                        ifmt = "{}s".format(nidx)

                        # Determine number of characters between two Es
                        i1 = line.find("E")
                        i2 = line.find("E", i1 + 1)

                        # Initialize data format
                        if i2 >= 0:
                            di = i2 - i1
                            dfmt = "{}.{}e".format(di, di - 7)
                            fmt = [ifmt] + 20 * [dfmt]  # Read 20 data columns at most
                        else:
                            fmt = [ifmt, "12.5e"]
                        fmt = ",".join(fmt)

                        first = False

                    tmp += read_record(line, fmt)
                    variables[-1].append([x for x in tmp if x is not None])

                line = f.readline()
                if line[1:].startswith("@@@@@"):
                    break

        elif _end_of_file(line):
            break

    return headers, times, variables


def _end_of_file(line):
    """Return True if last line."""
    return line.startswith("END OF TOUGH2 SIMULATION") or line.startswith(
        "END OF TOUGH3 SIMULATION"
    )
