from __future__ import with_statement

import numpy

from .._common import to_output
from ....mesh.tecplot._tecplot import _read_variables, _read_zone

__all__ = [
    "read",
    "write",
]


def read(filename, file_type, file_format, labels_order):
    """Read OUTPUT_ELEME.tec."""
    with open(filename, "r") as f:
        # Look for header (VARIABLES)
        while True:
            line = f.readline().strip()
            if line.upper().startswith("VARIABLES"):
                break

        # Read header (VARIABLES)
        headers = _read_variables(line)

        # Loop until end of file
        times, labels, variables = [], [], []
        line = f.readline().upper().strip()
        while True:
            # Read zone
            if line.startswith("ZONE"):
                zone = _read_zone(line)
                zone["T"] = (
                    float(zone["T"].split()[0]) if "T" in zone.keys() else None
                )
                if "I" not in zone.keys():
                    raise ValueError()

            # Read data
            data = []
            for _ in range(zone["I"]):
                line = f.readline().strip()
                data.append([float(x) for x in line.split()])
            data = numpy.array(data)

            # Output
            times.append(zone["T"])
            labels.append(None)
            variables.append(data)

            line = f.readline().upper().strip()
            if not line:
                break

    return to_output(file_type, file_format, labels_order, headers, times, labels, variables)


def write(filename):
    """Write OUTPUT_ELEME.tec."""
    pass
