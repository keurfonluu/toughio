from __future__ import with_statement

import numpy

from .._common import to_output

__all__ = [
    "read",
    "write",
]

header_to_unit = {
    "ELEM": "",
    "X": "(M)",
    "Y": "(M)",
    "Z": "(M)",
    "PRES": "(PA)",
    "TEMP": "(DEC-C)",
    "PCAP_GL": "(PA)",
    "DEN_G": "(KG/M**3)",
    "DEN_L": "(KG/M**3)",
    "ELEM1": "",
    "ELEM2": "",
    "HEAT": "(W)",
    "FLOW": "(KG/S)",
    "FLOW_G": "(KG/S)",
    "FLOW_L": "(KG/S)",
}


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
    out = output[-1]
    headers = ["ELEM"] if out.type == "element" else ["ELEM1", "ELEM2"]
    headers += ["X"] if "X" in out.data.keys() else []
    headers += ["Y"] if "Y" in out.data.keys() else []
    headers += ["Z"] if "Z" in out.data.keys() else []
    headers += [k for k in out.data.keys() if k not in {"X", "Y", "Z"}]

    with open(filename, "w") as f:
        _write_csv(f, output, headers)


def _write_csv(f, output, headers):
    """Write CSV table."""
    # Headers
    units = [header_to_unit[header] if header in header_to_unit.keys() else " (-)" for header in headers]
    f.write(",".join('"{:>18}"'.format(header) for header in headers) + "\n")
    f.write(",".join('"{:>18}"'.format(unit) for unit in units) + "\n")

    # Data
    formats = [
        '"{:>18}"'
        if header.startswith("ELEM")
        else "{:20.12e}"
        for header in headers
    ]
    for out in output:
        # Time step
        f.write('"TIME [sec]  {:.8e}"\n'.format(out.time))

        # Table
        for i, label in enumerate(out.labels):
            record = [label] if isinstance(label, str) else [l for l in label]
            record += [out.data[k][i] for k in headers if not k.startswith("ELEM")]
            record = ",".join(fmt.format(rec) for fmt, rec in zip(formats, record)) + "\n"
            f.write(record)
