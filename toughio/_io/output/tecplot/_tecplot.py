import numpy as np

from ...._common import open_file
from .._common import to_output

__all__ = [
    "read",
    "write",
]


zone_key_to_type = {
    "T": str,
    "I": int,
    "J": int,
    "K": int,
    "C": str,
    "N": int,
    "NODES": int,
    "E": int,
    "ELEMENTS": int,
    "F": str,
    "ET": str,
    "DATAPACKING": str,
    "ZONETYPE": str,
    "NV": int,
    "VARLOCATION": str,
}


def read(filename, file_type, file_format, labels_order):
    """
    Read OUTPUT_ELEME.tec.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_type : str
        Input file type.
    file_format : str
        Input file format.
    labels_order : list of array_like
        List of labels.

    Returns
    -------
    namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step.

    """
    with open_file(filename, "r") as f:
        headers, zones = read_buffer(f)

    times, labels, variables = [], [], []
    for zone in zones:
        time = float(zone["title"].split()[0]) if "title" in zone else None

        times.append(time)
        labels.append([])
        variables.append(zone["data"])

    return to_output(
        file_type, file_format, labels_order, headers, times, labels, variables
    )


def read_buffer(f):
    """Read OUTPUT_ELEME.tec."""
    zones = []

    # Loop until end of file
    while True:
        line = f.readline().strip()

        # Read header (VARIABLES)
        if line.upper().startswith("VARIABLES"):
            headers = _read_variables(line)

        # Read zone
        elif line.upper().startswith("ZONE"):
            zone = _read_zone(line)

            if "I" not in zone:
                raise ValueError()

            # Read data
            data = np.genfromtxt(f, max_rows=zone["I"])

            # Output
            tmp = {"data": data}
            tmp["title"] = zone["T"]
            zones.append(tmp)

        elif not line:
            break

    return headers, zones


def write(filename, output):
    """
    Write OUTPUT_ELEME.tec.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    output : namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step to export.

    """
    out = output[-1]
    headers = []

    if "X" in out.data:
        headers += ["X"]

    else:
        raise ValueError()

    if "Y" in out.data:
        headers += ["Y"]

    else:
        raise ValueError()

    headers += ["Z"] if "Z" in out.data else []
    headers += [k for k in out.data if k not in {"X", "Y", "Z"}]

    with open_file(filename, "w") as f:
        # Headers
        record = "".join(f"{header:>18}" for header in headers)
        f.write(f" VARIABLES       ={record}\n")

        # Data
        for out in output:
            # Zone
            record = f' ZONE T="{out.time:14.7e} SEC"  I = {len(out.data["X"]):8d}'
            f.write(f"{record}\n")

            # Table
            data = np.transpose([out.data[k] for k in headers])
            for d in data:
                record = "".join(f"{x:20.12e}" for x in d)
                f.write(f"{' ' * 18}{record}\n")


def _read_variables(line):
    # Gather variables in a list
    line = line.split("=")[1]
    line = [x for x in line.replace(",", " ").split()]
    variables = []

    i = 0
    while i < len(line):
        if '"' in line[i] and not (line[i].startswith('"') and line[i].endswith('"')):
            var = f"{line[i]} {line[i + 1]}"
            i += 1

        else:
            var = line[i]

        variables.append(var.replace('"', ""))
        i += 1

    return [variable for variable in variables if variable]


def _read_zone(line):
    # Gather zone entries in a dict
    line = line[5:]
    zone = {}

    # Look for zone title
    ivar = line.find('"')

    # If zone contains a title, process it and save the title
    if ivar >= 0:
        i1, i2 = ivar, ivar + line[ivar + 1 :].find('"') + 2
        zone_title = line[i1 + 1 : i2 - 1]
        line = line.replace(line[i1:i2], "PLACEHOLDER")

    else:
        zone_title = None

    # Look for VARLOCATION (problematic since it contains both ',' and '=')
    ivar = line.find("VARLOCATION")

    # If zone contains VARLOCATION, process it and remove the key/value pair
    if ivar >= 0:
        i1, i2 = line.find("("), line.find(")")
        zone["VARLOCATION"] = line[i1 : i2 + 1].replace(" ", "")
        line = line[:ivar] + line[i2 + 1 :]

    # Split remaining key/value pairs separated by '='
    line = [x for x in line.replace(",", " ").split() if x != "="]
    i = 0
    while i < len(line) - 1:
        if "=" in line[i]:
            if not (line[i].startswith("=") or line[i].endswith("=")):
                key, value = line[i].split("=")

            else:
                key = line[i].replace("=", "")
                value = line[i + 1]
                i += 1

        else:
            key = line[i]
            value = line[i + 1].replace("=", "")
            i += 1

        zone[key] = zone_key_to_type[key](value)
        i += 1

    # Add zone title to zone dict
    if zone_title:
        zone["T"] = zone_title.strip()

    return zone
