import numpy as np

from ...._common import open_file
from .._common import to_output

__all__ = [
    "read",
    "write",
]


def read(filename, file_type, file_format, labels_order):
    """Read Petrasim OUTPUT_ELEME.csv."""
    with open_file(filename, "r") as f:
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

    times = np.array(times)
    elements = np.array(elements)
    data = np.array(data)

    labels, unique_times, variables = [], [], []
    for time in np.unique(times):
        idx = times == time
        labels.append(elements[idx])
        unique_times.append(time)
        variables.append(data[idx])

    return to_output(
        file_type, file_format, labels_order, headers, unique_times, labels, variables
    )


def write(filename, output):
    """Write Petrasim OUTPUT_ELEME.csv."""
    out = output[-1]
    headers = []
    headers += ["X"] if "X" in out.data else []
    headers += ["Y"] if "Y" in out.data else []
    headers += ["Z"] if "Z" in out.data else []
    headers += [k for k in out.data if k not in {"X", "Y", "Z"}]

    with open_file(filename, "w") as f:
        # Headers
        record = ",".join(
            f"{header:>18}" for header in ["TIME [sec]", "ELEM", "INDEX"] + headers
        )
        f.write(f"{record}\n")

        # Data
        for out in output:
            data = np.transpose([out.data[k] for k in headers])
            formats = ["{:20.12e}", "{:>18}", "{:20d}"]
            formats += ["{:20.12e}"] * len(out.data)

            i = 0
            for d in data:
                tmp = [out.time, out.labels[i], i + 1]
                tmp += [x for x in d]
                record = ",".join(fmt.format(x) for fmt, x in zip(formats, tmp))
                f.write(f"{record}\n")
                i += 1
