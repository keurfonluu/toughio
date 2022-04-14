from ...._common import open_file
from ...._exceptions import ReadError
from ...._helpers import FileIterator

__all__ = [
    "read",
]


def read(filename):
    """
    Read TOUGHREACT solute input file.

    Parameters
    ----------
    filename : str
        Input file name.

    """
    with open_file(filename, "r") as f:
        out = read_buffer(f)

    return out


def read_buffer(f):
    """Read TOUGHREACT solute input file."""
    parameters = {}
    fiter = FileIterator(f)

    try:
        parameters.update(_read_title(fiter))
        parameters.update(_read_options(fiter))
        parameters.update(_read_filenames(fiter))

    except:
        raise ReadError("failed to parse line {}.".format(fiter.count))

    return parameters


def _read_title(f):
    """Read title."""
    line = f.next(skip_empty=True, comments="#").strip()
    
    return {"title": line}


def _read_options(f):
    """Read options."""
    # Record 2
    line = f.next(skip_empty=True, comments="#").strip()
    data = [int(x) for x in line.split()]
    if len(data) < 8:
        raise ReadError()

    options = {
        "options": {
            "flags": {
                "iteration_scheme": data[0],
                "reactive_surface_area": data[1],
                "solver": data[2],
                "n_subiteration": data[3],
                "gas_transport": data[4],
                "verbosity": data[5],
                "feedback": data[6],
                "coupling": data[7],
                # ITDS_REACT is not used
            }
        }
    }

    # Record 3
    line = f.next(skip_empty=True, comments="#").strip()
    data = [float(x) for x in line.split()]
    if len(data) < 4:
        raise ReadError()

    options["options"].update({
        "sl_min": data[0],
        "rcour": data[1],
        "ionic_strength_max": data[2],
        "mineral_gas_factor": data[3],
    })

    return options


def _read_filenames(f):
    """Read file names."""
    filenames = {"files": {}}

    line = f.next(skip_empty=True, comments="#")
    filenames["files"]["thermodynamic_input"] = line[:20].strip()

    for keys in {"iteration", "plot", "solid", "gas", "time"}:
        line = f.next()
        filenames["files"]["{}_output".format(keys)] = line[:20].strip()

    return filenames
