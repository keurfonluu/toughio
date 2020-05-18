from __future__ import with_statement

import numpy

from .._common import Output
from ...input.tough._helpers import str2float

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order):
    """Read standard TOUGH OUTPUT."""
    out = []
    with open(filename, "r") as f:
        for line in f:
            line = line.upper().strip()
            if line.startswith("OUTPUT DATA AFTER"):
                out.append(_read_table(f))

    return out


def _read_table(f):
    """Read data table for current time step."""
    # Look for "TOTAL TIME"
    while True:
        line = next(f).strip()
        if line.startswith("TOTAL TIME"):
            break

    # Read time step in following line
    line = next(f).strip()
    time = float(line.split()[0])

    # Look for "ELEM."
    while True:
        line = next(f).strip()
        if line.startswith("ELEM."):
            break

    # Read headers once (ignore "ELEM." and "INDEX")
    headers = line.split()[2:]

    # Look for next non-empty line
    while True:
        line = next(f)
        if line.strip():
            break

    # Loop until end of output block
    variables, labels = [], []
    while True:
        if line[:10].strip() and not line.strip().startswith("ELEM"):
            line = line.strip()
            labels.append(line[:5])
            variables.append([str2float(x) for x in line[5:].split()[1:]])

        line = next(f)
        if line[1:].startswith("@@@@@"):
            break

    return Output(
        "element", "tough", time, numpy.array(labels), {k: v for k, v in zip(headers, numpy.transpose(variables))}
    )
        

