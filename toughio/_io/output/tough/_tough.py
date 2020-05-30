from __future__ import with_statement

import numpy

from ...input.tough._helpers import str2float
from .._common import to_output

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order):
    """Read standard TOUGH OUTPUT."""
    with open(filename, "r") as f:
        headers, times, variables = _read_table(f, file_type)

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


def _read_table(f, file_type):
    """Read data table for current time step."""
    labels_key = "ELEM." if file_type == "element" else "ELEM1"
    ilab = 1 if file_type == "element" else 2

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
                    line = line.strip()
                    tmp = (
                        [line[:5]] if file_type == "element" else [line[:5], line[7:12]]
                    )
                    tmp += [str2float(l) for l in line[6 * ilab :].split()]
                    variables[-1].append(tmp)

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
