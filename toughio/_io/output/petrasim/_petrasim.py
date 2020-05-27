from __future__ import with_statement

import numpy

from .._common import to_output

__all__ = [
    "read",
    "write",
]


def read(filename, file_type, file_format, labels_order):
    """Read Petrasim OUTPUT_ELEME.csv."""
    with open(filename, "r") as f:
        # Headers
        line = f.readline().strip()
        headers = [header.strip() for header in line.split(",")[3:]]

        # Data
        times, elements, data = [], [], []
        while True:
            line = f.readline().strip()

            if line:
                line = line.split(",")
                times.append(float(line[0]))
                elements.append(line[1].strip())
                data.append([float(x) for x in line[3:]])
            else:
                break

    times = numpy.array(times)
    elements = numpy.array(elements)
    data = numpy.array(data)

    labels, unique_times, variables = [], [], []
    for time in numpy.sort(numpy.unique(times)):
        idx = times == time
        labels.append(elements[idx])
        unique_times.append(time)
        variables.append(data[idx])

    return to_output(file_type, file_format, labels_order, headers, unique_times, labels, variables)


def write(filename, output):
    """Write Petrasim OUTPUT_ELEME.csv."""
    pass
