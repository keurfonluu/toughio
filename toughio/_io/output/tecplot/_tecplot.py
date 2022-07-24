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
    """Read OUTPUT_ELEME.tec."""
    with open_file(filename, "r") as f:
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
                zone["T"] = float(zone["T"].split()[0]) if "T" in zone else None
                if "I" not in zone:
                    raise ValueError()

            # Read data
            data = []
            for _ in range(zone["I"]):
                line = f.readline().strip()
                data.append([float(x) for x in line.split()])
            data = np.array(data)

            # Output
            times.append(zone["T"])
            labels.append(None)
            variables.append(data)

            line = f.readline().upper().strip()
            if not line:
                break

    return to_output(
        file_type, file_format, labels_order, headers, times, labels, variables
    )


def write(filename, output):
    """Write OUTPUT_ELEME.tec."""
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
            var = f"{line[i]}_{line[i + 1]}"
            i += 1
        else:
            var = line[i]

        variables.append(var.replace('"', ""))
        i += 1

    # Check that at least X and Y are defined
    if "X" not in variables and "x" not in variables:
        raise ValueError("Variable 'X' not found")
    if "Y" not in variables and "y" not in variables:
        raise ValueError("Variable 'Y' not found")

    return variables


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
        zone["T"] = zone_title

    return zone
