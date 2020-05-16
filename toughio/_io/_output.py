from __future__ import with_statement

import numpy

from . import tough

__all__ = [
    "get_output_type",
    "read_eleme",
    "read_conne",
    "read_save",
]


def get_output_type(filename):
    """Get output file type and format."""
    with open(filename, "r") as f:
        line = f.readline().strip()

    if line.startswith("INCON"):
        return "save", "tough"
    elif "=" in line:
        return "element", "tecplot"
    else:
        header = line.split(",")[0].replace('"', "").strip()
        
        if header == "ELEM":
            return "element", "tough"
        elif header == "ELEM1":
            return "connection", "tough"
        else:
            raise ValueError()


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
    headers, times, variables = _read_csv(f, "element")

    headers = headers[1:]
    labels = [[v[0] for v in variable] for variable in variables]
    variables = numpy.array([[v[1:] for v in variable] for variable in variables])
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


def read_conne(filename):
    """Read OUTPUT_CONNE.csv."""
    with open(filename, "r") as f:
        headers, times, variables = _read_csv(f, "connection")

    headers = headers[2:]
    labels = [[v[:2] for v in variable] for variable in variables]
    variables = numpy.array([[v[2:] for v in variable] for variable in variables])
    return headers, times, labels, variables


def read_save(filename, labels_order):
    """Read SAVE."""
    parameters = tough.read(filename)

    labels = list(parameters["initial_conditions"].keys())
    variables = [v["values"] for v in parameters["initial_conditions"].values()]

    data = {"X{}".format(i + 1): x for i, x in enumerate(numpy.transpose(variables))}

    data["porosity"] = numpy.array(
        [v["porosity"] for v in parameters["initial_conditions"].values()]
    )

    userx = [
        v["userx"]
        for v in parameters["initial_conditions"].values()
        if "userx" in v.keys()
    ]
    if userx:
        data["userx"] = numpy.array(userx)

    labels_order = (
        labels_order if labels_order else parameters["initial_conditions_order"]
    )
    return numpy.array(labels), data, labels_order


def _read_csv(f, file_type):
    """Read OUTPUT_{ELEME, CONNE}.csv."""    
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
