from pytest import param
from ...._common import open_file
from ...._exceptions import ReadError
from ...._helpers import FileIterator
from ..tough._helpers import read_record, prune_nones_list

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
        parameters["options"].update(_read_weights_coefficients(fiter))
        parameters["options"].update(_read_convergence(fiter))

        output, numbers = _read_output(fiter)
        parameters["options"].update(output["options"])
        parameters["flags"].update(output["flags"])

        parameters["output"] = {}
        elements = _read_elements(fiter, numbers["NWNOD"])
        if elements:
            parameters["output"]["elements"] = elements

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

    # Record 3
    line = f.next(skip_empty=True, comments="#").strip()
    data = [float(x) for x in line.split()]
    if len(data) < 4:
        raise ReadError()

    options["options"] = {
        "sl_min": data[0],
        "rcour": data[1],
        "ionic_strength_max": data[2],
        "mineral_gas_factor": data[3],
    }

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


def _read_weights_coefficients(f):
    """Read weights and diffusion coefficients."""
    line = f.next(skip_empty=True, comments="#").strip()
    data = [float(x) for x in line.split()]
    if len(data) < 4:
        raise ReadError()

    options = {
        "w_time": data[0],
        "w_upstream": data[1],
        "aqueous_diffusion_coefficient": data[2],
        "molecular_diffusion_coefficient": data[3],
    }

    return options


def _read_convergence(f):
    """Read convergence criterion."""
    line = f.next(skip_empty=True, comments="#").strip()
    data = line.split()
    if len(data) < 7:
        raise ReadError()

    options = {
        "n_iteration_tr": int(data[0]),
        "eps_tr": float(data[1]),
        "n_iteration_ch": int(data[2]),
        "eps_ch": float(data[3]),
        "eps_mb": float(data[4]),
        "eps_dc": float(data[5]),
        "eps_dr": float(data[6]),
    }

    return options


def _read_output(f):
    """Read output control variables."""
    output = {"options": {}, "flags": {}}

    line = f.next(skip_empty=True, comments="#").strip()
    data = [int(x) for x in line.split()]
    if len(data) < 10:
        raise ReadError()

    output = {
        "options": {"n_cycle_print": data[0]},
        "flags": {
            "aqueous_concentration_unit": data[7],
            "mineral_unit": data[8],
            "gas_concentration_unit": data[9],
        },
    }

    numbers = {
        "NWNOD": data[1],
        "NWCOM": data[2],
        "NWMIN": data[3],
        "NWAQ": data[4],
        "NWADS": data[5],
        "NWEXC": data[6],
    }

    return output, numbers


def _read_elements(f, n):
    """Read list of grid blocks."""
    elements = []

    if n > 0:
        fmt = ",".join(15 * ["5s"])
        line = f.next(skip_empty=True, comments="#").strip()
        data = read_record(line, fmt)
        elements += data

        while len(elements) < n:
            line = f.next().strip()
            data = read_record(line, fmt)
            elements += data

        return prune_nones_list(elements[:n])

    elif n < 0:
        line = f.next(skip_empty=True, comments="#").strip()
        elements.append(line[:5])
        while True:
            line = f.next().strip()

            if line:
                elements.append(line[:5])

            else:
                break

        return elements

    else:
        _ = f.next(comments="#")  # Skip next blank line
