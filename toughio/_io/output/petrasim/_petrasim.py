import numpy as np

from ...._common import open_file
from .._common import to_output, ElementOutput

__all__ = [
    "read",
    "write",
]


def read(filename, file_type, labels_order=None, time_steps=None):
    """
    Read Petrasim OUTPUT_ELEME.csv.

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
    if time_steps is not None:
        if isinstance(time_steps, int):
            time_steps = [time_steps]

        if any(i < 0 for i in time_steps):
            n_steps = _count_time_steps(filename)
            time_steps = [i if i >= 0 else n_steps + i for i in time_steps]
        
        time_steps = set(time_steps)

    with open_file(filename, "r") as f:
        # Label index
        ilab = 3 if file_type == "element" else 4

        # Headers
        line = f.readline().strip()
        headers = [header.strip() for header in line.split(",")[ilab:]]

        # Data
        t_step = -1
        count, tcur, offset = 0, None, []
        times, labels, data = [], [], []

        while True:
            line = f.readline().strip()

            if line:
                line = line.split(",")

                if line[0] != tcur:
                    t_step += 1

                    if time_steps is not None and t_step > max(time_steps):
                        break

                    tcur = line[0]

                    if time_steps is None or t_step in time_steps:
                        offset.append(count)
                        times.append(float(tcur))

                if time_steps is None or t_step in time_steps:
                    if file_type == "element":
                        labels.append(line[1].strip())

                    else:
                        labels.append([line[1].strip(), line[2].strip()])

                    data.append([float(x) for x in line[ilab:]])
                    count += 1

            else:
                break

        offset.append(count)

    return to_output(
        file_type,
        labels_order,
        headers,
        times,
        [labels[i1:i2] for i1, i2 in zip(offset[:-1], offset[1:])],
        [data[i1:i2] for i1, i2 in zip(offset[:-1], offset[1:])],
    )


def write(filename, output):
    """
    Write Petrasim OUTPUT_ELEME.csv.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    output : namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step to export.

    """
    out = output[-1]
    headers = []
    headers += ["X"] if "X" in out.data else []
    headers += ["Y"] if "Y" in out.data else []
    headers += ["Z"] if "Z" in out.data else []
    headers += [k for k in out.data if k not in {"X", "Y", "Z"}]

    with open_file(filename, "w") as f:
        # Headers
        headers_ = (
            ["TIME [sec]", "ELEM", "INDEX"]
            if isinstance(out, ElementOutput)
            else ["TIME [sec]", "ELEM1", "ELEM2", "INDEX"]
        )
        record = ",".join(
            f"{header:>18}" for header in headers_ + headers
        )
        f.write(f"{record}\n")

        # Data
        for out in output:
            data = np.transpose([out.data[k] for k in headers])
            formats = (
                ["{:20.12e}", "{:>18}", "{:20d}"]
                if isinstance(out, ElementOutput)
                else ["{:20.12e}", "{:>18}", "{:>18}", "{:20d}"]
            )
            formats += ["{:20.12e}"] * len(out.data)

            i = 0
            for d in data:
                tmp = (
                    [out.time, out.labels[i], i + 1]
                    if isinstance(out, ElementOutput)
                    else [out.time, *out.labels[i], i + 1]
                )
                tmp += [x for x in d]
                record = ",".join(fmt.format(x) for fmt, x in zip(formats, tmp))
                f.write(f"{record}\n")
                i += 1


def _count_time_steps(filename):
    """Count the number of time steps."""
    with open_file(filename, "r") as f:
        x = np.genfromtxt(f, delimiter=",", skip_header=1, usecols=0)

    return np.unique(x).size
