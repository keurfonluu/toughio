from __future__ import with_statement

import numpy

from .._common import to_output
from ...input.tough._helpers import str2float

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order):
    """Read standard TOUGH OUTPUT."""
    with open(filename, "r") as f:
        headers, times, variables = _read_table(f)

        headers = headers[2:]
        labels = [[v[0] for v in variable] for variable in variables]
        variables = numpy.array([[v[2:] for v in variable] for variable in variables])

    return to_output(file_type, file_format, labels_order, headers, times, labels, variables)


def _read_table(f):
    """Read data table for current time step."""
    times, variables = [], []
    while True:
        line = f.readline().strip()

        # Look for "TOTAL TIME"
        if line.startswith("TOTAL TIME"):
            # Read time step in following line
            line = f.readline().strip()
            times.append(float(line.split()[0]))
            variables.append([])

            # Look for "ELEM."
            while True:
                line = f.readline().strip()
                if line.startswith("ELEM."):
                    break

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
                    tmp = [line[:5]]
                    tmp += [str2float(x) for x in line[5:].split()]
                    variables[-1].append(tmp)

                line = f.readline()
                if line[1:].startswith("@@@@@"):
                    break

        elif line.startswith("END OF TOUGH"):
            break

    return headers, times, variables
