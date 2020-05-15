from __future__ import with_statement

import numpy

__all__ = [
    "read_eleme",
]


def read_eleme(filename, file_format):
    """Read OUTPUT_ELEME.{csv, tec}."""
    with open(filename, "r") as f:
        return (
            read_eleme_csv(f)
            if file_format == "tough"
            else read_eleme_tecplot(f)
        )


def read_eleme_csv(f):
    """Read OUTPUT_ELEME.csv."""
    # Read header
    line = f.readline().replace('"', "")
    headers = [l.strip() for l in line.split(",")]
    headers = headers[1:]

    # Skip second line (unit)
    line = f.readline()

    # Check third line (does it start with TIME?)
    line = f.readline()
    single = not line.startswith('"TIME')

    # Read data
    if single:
        times, labels, variables = [None], [[]], [[]]
    else:
        times, labels, variables = [], [], []

    line = line.replace('"', "").strip()
    while line:
        line = line.split(",")

        # Time step
        if line[0].startswith("TIME"):
            line = line[0].split()
            times.append(float(line[-1]))
            variables.append([])
            labels.append([])

        # Output
        else:
            labels[-1].append(line[0].strip())
            variables[-1].append([float(l.strip()) for l in line[1:]])

        line = f.readline().strip().replace('"', "")

    return headers, times, labels, variables


def read_eleme_tecplot(f):
    """Read OUTPUT_ELEME.tec."""
    from ..mesh.tecplot._tecplot import _read_variables, _read_zone

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
        # Python 2.7 does not allow mix of for and while loops when reading a file
        # data = numpy.genfromtxt(f, max_rows=zone["I"])
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

    return headers, times, labels, variables
