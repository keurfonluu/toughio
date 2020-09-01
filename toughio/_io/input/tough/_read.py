from __future__ import division, with_statement

from ...._common import block_to_format, get_label_length
from ._helpers import prune_nones_dict, prune_nones_list, read_record

__all__ = [
    "read",
]


def read(filename, label_length=None):
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str
        Input file name.
    label_length : int or None, optional, default None
        Number of characters in cell labels.

    Returns
    -------
    dict
        TOUGH input parameters.

    """
    if not (label_length is None or isinstance(label_length, int)):
        raise TypeError()
    if isinstance(label_length, int) and not 5 <= label_length < 10:
        raise ValueError()

    with open(filename, "r") as f:
        out = read_buffer(f, label_length)

    return out


def read_buffer(f, label_length):
    """Read TOUGH input file."""
    parameters = {}

    # Title
    line = f.readline().strip()
    if line[:5] not in {"ROCKS", "ELEME", "INCON", "GENER"}:
        title = [line]
        while True:
            line = f.readline().strip()
            if not line.startswith("ROCKS"):
                title.append(line)
            else:
                break

        parameters["title"] = title[0] if len(title) == 1 else title
    f.seek(0)

    # Loop over blocks
    # Some blocks (INCON, INDOM, PARAM) need to rewind to previous line but tell and seek are disabled by next
    # See <https://stackoverflow.com/questions/22688505/is-there-a-way-to-go-back-when-reading-a-file-using-seek-and-calls-to-next>
    fiter = iter(f.readline, "")
    for line in fiter:
        if line.startswith("ROCKS"):
            parameters.update(_read_rocks(fiter))
        elif line.startswith("RPCAP"):
            rpcap = _read_rpcap(fiter)
            if "default" in parameters.keys():
                parameters["default"].update(rpcap)
            else:
                parameters["default"] = rpcap
        elif line.startswith("FLAC"):
            flac = _read_flac(fiter, parameters["rocks_order"])
            parameters["flac"] = flac["flac"]
            for k, v in flac["rocks"].items():
                parameters["rocks"][k].update(v)
        elif line.startswith("MULTI"):
            parameters.update(_read_multi(fiter))
        elif line.startswith("SELEC"):
            parameters.update(_read_selec(fiter))
        elif line.startswith("SOLVR"):
            parameters.update(_read_solvr(fiter))
        elif line.startswith("START"):
            parameters["start"] = True
        elif line.startswith("PARAM"):
            param = _read_param(fiter, f)
            parameters["options"] = param["options"]
            parameters["extra_options"] = param["extra_options"]
            if "default" in parameters.keys():
                parameters["default"].update(param["default"])
            else:
                parameters["default"] = param["default"]
        elif line.startswith("INDOM"):
            indom = _read_indom(fiter, f)
            for k, v in indom["rocks"].items():
                parameters["rocks"][k].update(v)
        elif line.startswith("MOMOP"):
            parameters.update(_read_momop(fiter))
        elif line.startswith("TIMES"):
            parameters.update(_read_times(fiter))
        elif line.startswith("FOFT"):
            parameters.update(_read_oft(fiter, "element_history"))
        elif line.startswith("COFT"):
            parameters.update(_read_oft(fiter, "connection_history"))
        elif line.startswith("GOFT"):
            parameters.update(_read_oft(fiter, "generator_history"))
        elif line.startswith("GENER"):
            parameters.update(_read_gener(fiter, label_length))
        elif line.startswith("DIFFU"):
            parameters.update(_read_diffu(fiter, f))
        elif line.startswith("OUTPU"):
            parameters.update(_read_outpu(fiter))
        elif line.startswith("ELEME"):
            parameters.update(_read_eleme(fiter, label_length))
            parameters["coordinates"] = False
        elif line.startswith("COORD"):
            coord = _read_coord(fiter)
            for k, v in zip(parameters["elements_order"], coord):
                parameters["elements"][k]["center"] = v
            parameters["coordinates"] = True
        elif line.startswith("CONNE"):
            parameters.update(_read_conne(fiter, label_length))
        elif line.startswith("INCON"):
            parameters.update(_read_incon(fiter, label_length, f))
        elif line.startswith("NOVER"):
            parameters["nover"] = True
        elif line.startswith("ENDCY"):
            break

    return parameters


def _read_rocks(f):
    """Read ROCKS block data."""
    fmt = block_to_format["ROCKS"]
    rocks = {"rocks": {}, "rocks_order": []}

    while True:
        line = next(f)

        if line.strip():
            # Record 1
            data = read_record(line, fmt[1])
            rock = data[0]
            rocks["rocks"][rock] = {
                "density": data[2],
                "porosity": data[3],
                "permeability": data[4] if len(set(data[4:7])) == 1 else data[4:7],
                "conductivity": data[7],
                "specific_heat": data[8],
            }

            nad = data[1]
            if nad is not None:
                # Record 2
                line = next(f)
                data = read_record(line, fmt[2])
                rocks["rocks"][rock].update(
                    {
                        "compressibility": data[0],
                        "expansivity": data[1],
                        "conductivity_dry": data[2],
                        "tortuosity": data[3],
                        "klinkenberg_parameter": data[4],
                        "distribution_coefficient_3": data[5],
                        "distribution_coefficient_4": data[6],
                    }
                )

            if nad and nad > 1:
                rocks["rocks"][rock].update(_read_rpcap(f))

            rocks["rocks_order"].append(rock)
        else:
            break

    rocks["rocks"] = {k: prune_nones_dict(v) for k, v in rocks["rocks"].items()}

    return rocks


def _read_rpcap(f):
    """Read RPCAP block data."""
    fmt = block_to_format["RPCAP"]
    rpcap = {}

    for key in ["relative_permeability", "capillarity"]:
        line = next(f)
        data = read_record(line, fmt)
        if data[0] is not None:
            rpcap[key] = {
                "id": data[0],
                "parameters": prune_nones_list(data[2:]),
            }

    return rpcap


def _read_flac(f, rocks_order):
    """Read FLAC block data."""
    fmt = block_to_format["FLAC"]
    flac = {"rocks": {}, "flac": {}}

    # Record 1
    line = next(f)
    data = read_record(line, fmt[1])
    flac["flac"]["creep"] = data[0]
    flac["flac"]["porosity_model"] = data[1]
    flac["flac"]["version"] = data[2]

    # Additional records
    for rock in rocks_order:
        flac["rocks"][rock] = {}

        line = next(f)
        data = read_record(line, fmt[2])
        flac["rocks"][rock]["permeability_model"] = {
            "id": data[0],
            "parameters": prune_nones_list(data[1:]),
        }

        line = next(f)
        data = read_record(line, fmt[3])
        flac["rocks"][rock]["equivalent_pore_pressure"] = {
            "id": data[0],
            "parameters": prune_nones_list(data[2:]),
        }

    flac["flac"] = prune_nones_dict(flac["flac"])

    return flac


def _read_multi(f):
    """Read MULTI block data."""
    fmt = block_to_format["MULTI"]
    multi = {}

    line = next(f)
    data = read_record(line, fmt)
    multi["n_component"] = data[0]
    multi["isothermal"] = data[1] == data[0]
    multi["n_phase"] = data[2]

    return multi


def _read_selec(f):
    """Read SELEC block data."""
    fmt = block_to_format["SELEC"]
    selec = {"selections": {}}

    line = next(f)
    data = read_record(line, fmt[1])
    selec["selections"]["integers"] = {k + 1: v for k, v in enumerate(data)}

    if selec["selections"]["integers"][1]:
        selec["selections"]["floats"] = []
        for _ in range(selec["selections"]["integers"][1]):
            line = next(f)
            data = read_record(line, fmt[2])
            selec["selections"]["floats"].append(prune_nones_list(data))

    selec["selections"]["integers"] = prune_nones_dict(selec["selections"]["integers"])
    if selec["selections"]["integers"][1] == 1:
        selec["selections"]["floats"] = selec["selections"]["floats"][0]

    return selec


def _read_solvr(f):
    """Read SOLVR block data."""
    fmt = block_to_format["SOLVR"]
    solvr = {}

    line = next(f)
    data = read_record(line, fmt)
    solvr["solver"] = {
        "method": data[0],
        "z_precond": data[2],
        "o_precond": data[4],
        "rel_iter_max": data[5],
        "eps": data[6],
    }

    return solvr


def _read_param(f, fh):
    """Read PARAM block data."""
    fmt = block_to_format["PARAM"]
    param = {}

    # Record 1
    line = next(f)
    data = read_record(line, fmt[1])
    param["options"] = {
        "n_iteration": data[0],
        "verbosity": data[1],
        "n_cycle": data[2],
        "n_second": data[3],
        "n_cycle_print": data[4],
        "temperature_dependence_gas": data[7],
        "effective_strength_vapor": data[8],
    }
    param["extra_options"] = {
        i + 1: int(x) for i, x in enumerate(data[5]) if x.isdigit()
    }

    # Record 2
    line = next(f)
    data = read_record(line, fmt[2])
    param["options"].update(
        {
            "t_ini": data[0],
            "t_max": data[1],
            "t_steps": data[2],
            "t_step_max": data[3],
            "gravity": data[5],
            "t_reduce_factor": data[6],
            "mesh_scale_factor": data[7],
        }
    )

    t_steps = int(data[2])
    if t_steps >= 0.0:
        param["options"]["t_steps"] = t_steps
    else:
        param["options"]["t_steps"] = []
        for _ in range(-t_steps):
            line = next(f)
            data = read_record(line, fmt[3])
            param["options"]["t_steps"] += prune_nones_list(data)
        if len(param["options"]["t_steps"]) == 1:
            param["options"]["t_steps"] = param["options"]["t_steps"][0]

    # Record 3
    line = next(f)
    data = read_record(line, fmt[4])
    param["options"].update(
        {
            "eps1": data[0],
            "eps2": data[1],
            "w_upstream": data[3],
            "w_newton": data[4],
            "derivative_factor": data[5],
        }
    )

    # Record 4 and record 5 (EOS7R)
    line = next(f)
    data = read_record(line, fmt[5])

    i = fh.tell()
    try:
        line = next(f)
        data += read_record(line, fmt[5])
    except ValueError:
        fh.seek(i)

    if any(x is not None for x in data):
        data = prune_nones_list(data)
        param["default"] = {"initial_condition": data}
    else:
        param["default"] = {}

    # Remove Nones
    param["options"] = prune_nones_dict(param["options"])
    param["extra_options"] = prune_nones_dict(param["extra_options"])

    return param


def _read_indom(f, fh):
    """Read INDOM block data."""
    fmt = block_to_format["INDOM"]
    indom = {"rocks": {}}

    line = next(f)
    two_lines = True
    while True:
        if line.strip():
            # Record 1
            rock = read_record(line, fmt[5])[0]

            # Record 2
            line = next(f)
            data = read_record(line, fmt[0])

            # Record 3 (EOS7R)
            if two_lines:
                i = fh.tell()
                line = next(f)

                if line.strip():
                    try:
                        data += read_record(line, fmt[0])
                    except ValueError:
                        two_lines = False
                        fh.seek(i)
                else:
                    fh.seek(i)

            data = prune_nones_list(data)
            indom["rocks"][rock] = {"initial_condition": data}
        else:
            break
        
        line = next(f)

    return indom


def _read_momop(f):
    """Read MOMOP block data."""
    fmt = block_to_format["MOMOP"]

    line = next(f)
    data = read_record(line, fmt)
    momop = {
        "more_options": {i + 1: int(x) for i, x in enumerate(data[0]) if x.isdigit()}
    }

    return momop


def _read_times(f):
    """Read TIMES block data."""
    fmt = block_to_format["TIMES"]
    times = {"times": []}

    # Record 1
    line = next(f)
    data = read_record(line, fmt[1])
    n_times = data[0]

    # Record 2
    while len(times["times"]) < n_times:
        line = next(f)
        data = read_record(line, fmt[2])
        times["times"] += prune_nones_list(data)

    if n_times == 1:
        times["times"] = times["times"][0]

    return times


def _read_oft(f, oft):
    """Read FOFT, COFT and GOFT blocks data."""
    history = {oft: []}

    while True:
        line = next(f).rstrip()

        if line:
            history[oft].append(line)
        else:
            break

    return history


def _read_gener(f, label_length):
    """Read GENER block data."""
    fmt = block_to_format["GENER"]
    gener = {"generators": {}}

    line = next(f)
    if not label_length:
        label_length = get_label_length(line[:9])

    while True:
        if line.strip():
            data = read_record(line, fmt[label_length])
            label = data[0]
            tmp = {
                "name": [data[1]],
                "nseq": [data[2]],
                "nadd": [data[3]],
                "nads": [data[4]],
                "type": [data[7]],
                "layer_thickness": [data[11]],
            }

            ltab = data[5]
            if ltab and ltab > 1:
                itab = data[8]
                keys = ["times", "rates"]
                keys += ["specific_enthalpy"] if itab else []
                for key in keys:
                    table = []

                    while len(table) < ltab:
                        line = next(f)
                        data = read_record(line, fmt[0])
                        table += prune_nones_list(data)

                    tmp[key] = [table]
            else:
                tmp.update(
                    {
                        "times": [None],
                        "rates": [data[9]],
                        "specific_enthalpy": [data[10]],
                    }
                )

            if label in gener["generators"].keys():
                for k, v in gener["generators"][label].items():
                    v += tmp[k]
            else:
                gener["generators"][label] = tmp
        else:
            break

        line = next(f)

    # Tidy up
    for generator in gener["generators"].values():
        for k, v in generator.items():
            if len(v) == 1:
                generator[k] = v[0]
            else:
                if all(x is None for x in v):
                    generator[k] = None

    return {
        k: {kk: prune_nones_dict(vv) for kk, vv in v.items()} for k, v in gener.items()
    }


def _read_diffu(f, fh):
    """Read DIFFU block data."""
    fmt = block_to_format["DIFFU"]
    diffu = {"diffusion": []}

    while True:
        i = fh.tell()
        line = next(f)

        if line.split():
            try:
                data = read_record(line, fmt)
                diffu["diffusion"].append(prune_nones_list(data))
            except ValueError:
                fh.seek(i)
                break
        else:
            break

    return diffu


def _read_outpu(f):
    """Read OUTPU block data."""
    fmt = block_to_format["OUTPU"]
    outpu = {"output": {}}

    # Format
    line = next(f).strip()
    if line and not line.isdigit():
        outpu["output"]["format"] = line if line else None
        line = next(f).strip()

    # Variables
    if line.isdigit():
        n_var = int(line)
        outpu["output"]["variables"] = {}

        for _ in range(n_var):
            line = next(f)
            data = read_record(line, fmt[3])
            name = data[0].lower()
            outpu["output"]["variables"][name] = prune_nones_list(data[1:])
            outpu["output"]["variables"][name] = (
                outpu["output"]["variables"][name]
                if len(outpu["output"]["variables"][name]) == 2
                else outpu["output"]["variables"][name][0]
                if len(outpu["output"]["variables"][name]) == 1
                else None
            )

    return outpu


def _read_eleme(f, label_length):
    """Read ELEME block data."""
    fmt = block_to_format["ELEME"]
    eleme = {"elements": {}, "elements_order": []}

    line = next(f)
    if not label_length:
        label_length = get_label_length(line[:9])

    while True:
        if line.strip():
            data = read_record(line, fmt[label_length])
            label = data[0]
            rock = data[3].strip()
            eleme["elements"][label] = {
                "nseq": data[1],
                "nadd": data[2],
                "material": int(rock) if all(r.isdigit() for r in rock) else rock,
                "volume": data[4],
                "heat_exchange_area": data[5],
                "permeability_modifier": data[6],
                "center": data[7:10],
            }

            eleme["elements_order"].append(label)
        else:
            break

        line = next(f)

    eleme["elements"] = {k: prune_nones_dict(v) for k, v in eleme["elements"].items()}

    return eleme


def _read_coord(f):
    """Read COORD block data."""
    fmt = block_to_format["COORD"]
    coord = []

    line = next(f)
    while True:
        if line.strip():
            data = read_record(line, fmt)
            coord.append(data)
        else:
            break

        line = next(f)

    return coord


def _read_conne(f, label_length):
    """Read CONNE block data."""
    fmt = block_to_format["CONNE"]
    conne = {"connections": {}, "connections_order": []}

    line = next(f)
    if not label_length:
        label_length = get_label_length(line[:9])

    while True:
        if line.strip() and not line.startswith("+++"):
            data = read_record(line, fmt[label_length])
            label = data[0]
            conne["connections"][label] = {
                "nseq": data[1],
                "nadd": data[2:4],
                "permeability_direction": data[4],
                "nodal_distances": data[5:7],
                "interface_area": data[7],
                "gravity_cosine_angle": data[8],
                "radiant_emittance_factor": data[9],
            }

            conne["connections_order"].append(label)
        else:
            break

        line = next(f)

    conne["connections"] = {
        k: prune_nones_dict(v) for k, v in conne["connections"].items()
    }

    return conne


def _read_incon(f, label_length, fh):
    """Read INCON block data."""
    fmt = block_to_format["INCON"]
    incon = {"initial_conditions": {}, "initial_conditions_order": []}

    line = next(f)
    if not label_length:
        label_length = get_label_length(line[:9])
    
    two_lines = True
    while True:
        if line.strip() and not line.startswith("+++"):
            # Record 1
            data = read_record(line, fmt[label_length])
            label = data[0]
            userx = prune_nones_list(data[4:9])
            incon["initial_conditions"][label] = {
                "porosity": data[3],
                "userx": userx if userx else None,
            }

            # Record 2
            line = next(f)
            data = read_record(line, fmt[0])

            # Record 3 (EOS7R)
            if two_lines:
                i = fh.tell()
                line = next(f)

                if line.strip() and not line.startswith("+++"):
                    try:
                        data += read_record(line, fmt[0])
                    except ValueError:
                        two_lines = False
                        fh.seek(i)
                else:
                    fh.seek(i)

            incon["initial_conditions"][label]["values"] = prune_nones_list(data)
            incon["initial_conditions_order"].append(label)
        else:
            break

        line = next(f)

    incon["initial_conditions"] = {
        k: prune_nones_dict(v) for k, v in incon["initial_conditions"].items()
    }

    return incon
