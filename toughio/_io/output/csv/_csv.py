from __future__ import with_statement

import numpy

from .._common import to_output

__all__ = [
    "read",
    "write",
]


def read(filename, file_type, file_format, labels_order):
    """Read OUTPUT_{ELEME, CONNE}.csv."""
    with open(filename, "r") as f:
        headers, times, labels, variables = (
            read_eleme(f)
            if file_type == "element"
            else read_conne(f)
        )

    return to_output(file_type, file_format, labels_order, headers, times, labels, variables)


def read_eleme(f):
    """Read OUTPUT_ELEME.csv."""
    headers, times, variables = _read_csv(f, "element")

    headers = headers[1:]
    labels = [[v[0] for v in variable] for variable in variables]
    variables = numpy.array([[v[1:] for v in variable] for variable in variables])
    return headers, times, labels, variables


def read_conne(f):
    """Read OUTPUT_CONNE.csv."""
    headers, times, variables = _read_csv(f, "connection")

    headers = headers[2:]
    labels = [[v[:2] for v in variable] for variable in variables]
    variables = numpy.array([[v[2:] for v in variable] for variable in variables])
    return headers, times, labels, variables


def _read_csv(f, file_type):
    """Read CSV table."""    
    # Read header
    line = f.readline().replace('"', "")
    headers = [l.strip() for l in line.split(",")]

    # Skip second line (unit)
    line = f.readline()

    # Check third line (does it start with TIME?)
    line = f.readline()
    single = not line.startswith('"TIME')

    # Read data
    if single:
        times, variables = [None], [[]]
    else:
        times, variables = [], []

    line = line.replace('"', "").strip()
    ilab = 1 if file_type == "element" else 2
    while line:
        line = line.split(",")

        # Time step
        if line[0].startswith("TIME"):
            line = line[0].split()
            times.append(float(line[-1]))
            variables.append([])

        # Output
        else:
            tmp = [l.strip() for l in line[:ilab]]
            tmp += [float(l.strip()) for l in line[ilab:]]
            variables[-1].append(tmp)

        line = f.readline().strip().replace('"', "")

    return headers, times, variables


def write(filename, output):
    """Write OUTPUT_{ELEME, CONNE}.csv."""
    pass


def write_eleme(f):
    """Write OUTPUT_ELEME.csv."""
    pass


def write_conne(f):
    """Write OUTTPUT_CONNE.csv."""
    pass


def _write_csv(f):
    """Write CSV table."""
    pass
