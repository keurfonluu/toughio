from ...._common import open_file
from ....core import ElementOutput
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


def read(filename, file_type, labels_order=None, time_steps=None):
    """
    Read OUTPUT_{ELEME, CONNE}.csv.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_type : str
        Input file type.
    labels_order : sequence of array_like
        List of labels. If None, output will be assumed ordered.
    time_steps : int or sequence of int
        List of time steps to read. If None, all time steps will be read.

    Returns
    -------
    :class:`toughio.ElementOutput`, :class:`toughio.ConnectionOutput`, sequence of :class:`toughio.ElementOutput` or sequence of :class:`toughio.ConnectionOutput`
        Output data for each time step.

    """
    return_list = True

    if time_steps is not None:
        if isinstance(time_steps, int):
            time_steps = [time_steps]
            return_list = False

        if any(i < 0 for i in time_steps):
            n_steps = _count_time_steps(filename)
            time_steps = [i if i >= 0 else n_steps + i for i in time_steps]

        time_steps = set(time_steps)

    with open_file(filename, "r") as f:
        headers, times, labels, data = _read_csv(f, file_type, time_steps)

    return to_output(
        file_type,
        labels_order,
        headers, times,
        labels,
        data,
        return_list,
    )


def _read_csv(f, file_type, time_steps=None):
    """Read CSV table."""
    # Label index
    ilab = 1 if file_type == "element" else 2

    # Read header
    line = f.readline().replace('"', "")
    headers = [l.strip() for l in line.split(",")[ilab:]]

    # Skip second line (unit)
    line = f.readline()

    # Check third line (does it start with TIME?)
    line = f.readline()
    single = not line.startswith('"TIME [sec]')

    # Read data
    if single:
        t_step = 0
        times, labels, data = [None], [[]], [[]]

    else:
        t_step = -1
        times, labels, data = [], [], []

    while line:
        line = line.split(",")

        # Time step
        if line[0].startswith('"TIME [sec]'):
            t_step += 1

            if time_steps is not None and t_step > max(time_steps):
                break

            if time_steps is None or t_step in time_steps:
                line = line[0].replace('"', "").split()
                times.append(float(line[-1]))
                labels.append([])
                data.append([])

        # Output
        elif time_steps is None or t_step in time_steps:
            if ilab == 1:
                labels[-1].append(line[0].replace('"', "").strip())

            else:
                labels[-1].append([l.replace('"', "").strip() for l in line[:ilab]])

            data[-1].append([float(l.strip()) for l in line[ilab:]])

        line = f.readline()

    return headers, times, labels, data


def write(filename, output, unit=None):
    """
    Write OUTPUT_{ELEME, CONNE}.csv.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    output : namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step to export.

    """
    if not (unit is None or isinstance(unit, dict)):
        raise TypeError()

    out = output[-1]
    headers = ["ELEM"] if isinstance(out, ElementOutput) else ["ELEM1", "ELEM2"]
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


def _count_time_steps(filename):
    """Count the number of time steps."""
    with open_file(filename, "r") as f:
        count = 0

        for line in f:
            count += int(line.startswith('"TIME [sec]'))

    return count
