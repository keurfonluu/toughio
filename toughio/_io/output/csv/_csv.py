import numpy as np

from ...._common import open_file
from .._common import to_output

__all__ = [
    "read",
    "write",
]

header_to_unit = {
    "ELEM": "",
    "X": "M",
    "Y": "M",
    "Z": "M",
    "PRES": "PA",
    "P": "PA",
    "TEMP": "DEC-C",
    "T": "DEC-C",
    "PCAP_GL": "PA",
    "PCAP": "PA",
    "DEN_G": "KG/M**3",
    "DG": "KG/M**3",
    "DEN_L": "KG/M**3",
    "DW": "KG/M**3",
    "ELEM1": "",
    "ELEM2": "",
    "HEAT": "W",
    "FLOW": "KG/S",
    "FLOW_G": "KG/S",
    "FLOW_L": "KG/S",
}


def read(filename, file_type, file_format, labels_order):
    """Read OUTPUT_{ELEME, CONNE}.csv."""
    with open_file(filename, "r") as f:
        headers, times, variables = _read_csv(f, file_type)

        ilab = 1 if file_type == "element" else 2
        headers = headers[ilab:]
        labels = [[v[:ilab] for v in variable] for variable in variables]
        labels = (
            [[l[0] for l in label] for label in labels]
            if file_type == "element"
            else labels
        )
        variables = np.array([[v[ilab:] for v in variable] for variable in variables])

    return to_output(
        file_type, file_format, labels_order, headers, times, labels, variables
    )


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


def write(filename, output, unit=None):
    """Write OUTPUT_{ELEME, CONNE}.csv."""
    if not (unit is None or isinstance(unit, dict)):
        raise TypeError()

    out = output[-1]
    headers = ["ELEM"] if out.type == "element" else ["ELEM1", "ELEM2"]
    headers += ["X"] if "X" in out.data else []
    headers += ["Y"] if "Y" in out.data else []
    headers += ["Z"] if "Z" in out.data else []
    headers += [k for k in out.data if k not in {"X", "Y", "Z"}]

    with open_file(filename, "w") as f:
        _write_csv(f, output, headers, unit)


def _write_csv(f, output, headers, unit=None):
    """Write CSV table."""
    header_to_unit_ = header_to_unit.copy()
    if unit is not None:
        header_to_unit_.update(unit)

    # Headers
    units = [
        header_to_unit_[header] if header in header_to_unit_ else "-"
        for header in headers
    ]
    f.write(",".join(f'"{header:>18}"' for header in headers) + "\n")
    f.write(",".join(f'"{f"({unit})":>18}"' for unit in units) + "\n")

    # Data
    formats = [
        '"{:>18}"' if header.startswith("ELEM") else "{:20.12e}" for header in headers
    ]
    for out in output:
        # Time step
        f.write(f'"TIME [sec]  {out.time:.8e}"\n')

        # Table
        for i, label in enumerate(out.labels):
            record = [label] if isinstance(label, str) else [l for l in label]
            record += [out.data[k][i] for k in headers if not k.startswith("ELEM")]
            record = (
                ",".join(
                    fmt.format(rec) if rec is not None else fmt.format(0.0)
                    for fmt, rec in zip(formats, record)
                )
                + "\n"
            )
            f.write(record)
