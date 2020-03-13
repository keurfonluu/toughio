from __future__ import division, with_statement

import logging

from ._helpers import prune_nones_dict, prune_nones_list, read_record

__all__ = [
    "read",
]


def read(filename):
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    dict
        TOUGH input parameters.

    """
    with open(filename, "r") as f:
        out = read_buffer(f)
    return out


def read_buffer(f):
    """Read TOUGH input file."""
    parameters = {}

    # Title
    parameters["title"] = f.readline().strip()

    # Loop over blocks
    while True:
        line = f.readline().strip()

        if line.startswith("ROCKS"):
            rocks, rocks_order = _read_rocks(f)
            parameters.update(rocks)
        elif line.startswith("RPCAP"):
            rpcap = _read_rpcap(f)
            if "default" in parameters.keys():
                parameters["default"].update(rpcap)
            else:
                parameters["default"] = rpcap
        elif line.startswith("FLAC"):
            flac = _read_flac(f, rocks_order)
            parameters["flac"] = flac["flac"]
            for k, v in flac["rocks"].items():
                parameters["rocks"][k].update(v)
        elif line.startswith("MULTI"):
            parameters.update(_read_multi(f))
        elif line.startswith("SELEC"):
            parameters.update(_read_selec(f))
        elif line.startswith("SOLVR"):
            parameters.update(_read_solvr(f))
        elif line.startswith("START"):
            parameters["start"] = True
        elif line.startswith("PARAM"):
            param = _read_param(f)
            parameters["options"] = param["options"]
            parameters["extra_options"] = param["extra_options"]
            if "default" in parameters.keys():
                parameters["default"].update(param["default"])
            else:
                parameters["default"] = param["default"]
        elif line.startswith("INDOM"):
            indom = _read_indom(f)
            for k, v in indom["rocks"].items():
                parameters["rocks"][k].update(v)
        elif line.startswith("MOMOP"):
            parameters.update(_read_momop(f))
        elif line.startswith("TIMES"):
            parameters.update(_read_times(f))
        elif line.startswith("FOFT"):
            parameters.update(_read_oft(f, "element_history"))
        elif line.startswith("COFT"):
            parameters.update(_read_oft(f, "connection_history"))
        elif line.startswith("GOFT"):
            parameters.update(_read_oft(f, "generator_history"))
        elif line.startswith("GENER"):
            parameters.update(_read_gener(f))
        elif line.startswith("DIFFU"):
            parameters.update(_read_diffu(f))
        elif line.startswith("OUTPU"):
            parameters.update(_read_outpu(f))
        elif line.startswith("ELEME"):
            logging.warning("Reading block ELEME is not supported. Skipping.")
        elif line.startswith("CONNE"):
            logging.warning("Reading block CONNE is not supported. Skipping.")
        elif line.startswith("INCON"):
            logging.warning("Reading block INCON is not supported. Skipping.")
        elif line.startswith("NOVER"):
            parameters["nover"] = True
        elif line.startswith("ENDCY"):
            break

    return parameters


def _read_rocks(f):
    """Read ROCKS block data."""
    rocks = {"rocks": {}}
    rocks_order = []

    while True:
        line = f.readline()

        if line.strip():
            # Record 1
            data = read_record(line, "5s,5d,10e,10e,10e,10e,10e,10e,10e")
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
                line = f.readline()
                data = read_record(line, "10e,10e,10e,10e,10e,10e,10e")
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

            rocks_order.append(rock)

        else:
            break

    rocks = {
        k: {kk: prune_nones_dict(vv) for kk, vv in v.items()} for k, v in rocks.items()
    }

    return rocks, rocks_order


def _read_rpcap(f):
    """Read RPCAP block data."""
    rpcap = {}

    for key in ["relative_permeability", "capillarity"]:
        line = f.readline()
        data = read_record(line, "5d,5s,10e,10e,10e,10e,10e,10e,10e")
        rpcap[key] = {
            "id": data[0],
            "parameters": prune_nones_list(data[2:]),
        }

    return rpcap


def _read_flac(f, rocks_order):
    """Read FLAC block data."""
    flac = {"rocks": {}, "flac": {}}

    # Record 1
    line = f.readline()
    data = read_record(line, ",".join(16 * ["5d"]))
    flac["flac"]["creep"] = data[0]
    flac["flac"]["porosity_model"] = data[1]
    flac["flac"]["version"] = data[2]

    # Additional records
    for rock in rocks_order:
        flac["rocks"][rock] = {}

        line = f.readline()
        data = read_record(line, "10d,10e,10e,10e,10e,10e,10e,10e")
        flac["rocks"][rock]["permeability_model"] = {
            "id": data[0],
            "parameters": prune_nones_list(data[1:]),
        }

        line = f.readline()
        data = read_record(line, "5d,5s,10e,10e,10e,10e,10e,10e,10e")
        flac["rocks"][rock]["equivalent_pore_pressure"] = {
            "id": data[0],
            "parameters": prune_nones_list(data[2:]),
        }

    flac["flac"] = prune_nones_dict(flac["flac"])

    return flac


def _read_multi(f):
    """Read MULTI block data."""
    multi = {}

    line = f.readline().split()
    multi["n_component"] = int(line[0])
    multi["isothermal"] = int(line[1]) == int(line[0])
    multi["n_phase"] = int(line[2])

    return multi


def _read_selec(f):
    """Read SELEC block data."""
    selec = {"selections": {}}

    line = f.readline()
    data = read_record(line, ",".join(16 * ["5d"]))
    selec["selections"]["integers"] = {k + 1: v for k, v in enumerate(data)}

    if selec["selections"]["integers"][1]:
        selec["selections"]["floats"] = []
        for _ in range(selec["selections"]["integers"][1]):
            line = f.readline()
            data = read_record(line, ",".join(8 * ["10e"]))
            selec["selections"]["floats"] += data

    selec["selections"]["integers"] = prune_nones_dict(selec["selections"]["integers"])
    if selec["selections"]["integers"][1]:
        selec["selections"]["floats"] = prune_nones_list(selec["selections"]["floats"])

    return selec


def _read_solvr(f):
    """Read SOLVR block data."""
    solvr = {}

    line = f.readline()
    data = read_record(line, "1d,2s,2s,3s,2s,10e,10e")
    solvr["solver"] = {
        "method": data[0],
        "z_precond": data[2],
        "o_precond": data[4],
        "rel_iter_max": data[5],
        "eps": data[6],
    }

    return solvr


def _read_param(f):
    """Read PARAM block data."""
    param = {}

    # Record 1
    line = f.readline()
    data = read_record(line, "2d,2d,4d,4d,4d,24S,10s,10e,10e")
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
    line = f.readline()
    data = read_record(line, "10e,10e,10f,10e,10s,10e,10e,10e")
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
            line = f.readline()
            data = read_record(line, "10e,10e,10e,10e,10e,10e,10e,10e")
            param["options"]["t_steps"] += prune_nones_list(data)
        if len(param["options"]["t_steps"]) == 1:
            param["options"]["t_steps"] = param["options"]["t_steps"][0]

    # Record 3
    line = f.readline()
    data = read_record(line, "10e,10e,10s,10e,10e,10e")
    param["options"].update(
        {
            "eps1": data[0],
            "eps2": data[1],
            "w_upstream": data[3],
            "w_newton": data[4],
            "derivative_factor": data[5],
        }
    )

    # Record 4
    line = f.readline()
    data = read_record(line, "20e,20e,20e,20e")
    if any(x is not None for x in data):
        data = prune_nones_list(data)
        param["default"] = {"initial_condition": data}
    else:
        param["default"] = {}

    # Remove Nones
    param["options"] = prune_nones_dict(param["options"])
    param["extra_options"] = prune_nones_dict(param["extra_options"])

    return param


def _read_indom(f):
    """Read INDOM block data."""
    indom = {"rocks": {}}

    while True:
        line = f.readline()

        if line.strip():
            rock = line[:5]
            line = f.readline()
            data = read_record(line, "20e,20e,20e,20e")
            data = prune_nones_list(data)
            indom["rocks"][rock] = {"initial_condition": data}
        else:
            break

    return indom


def _read_momop(f):
    """Read MOMOP block data."""
    line = f.readline()
    data = read_record(line, "40S")
    momop = {
        "more_options": {i + 1: int(x) for i, x in enumerate(data[0]) if x.isdigit()}
    }

    return momop


def _read_times(f):
    """Read TIMES block data."""
    times = {"times": []}

    # Record 1
    line = f.readline()
    data = read_record(line, "5d,5d,10e,10e")
    n_times = data[0]

    # Record 2
    while len(times["times"]) < n_times:
        line = f.readline()
        data = read_record(line, "10e,10e,10e,10e,10e,10e,10e,10e")
        times["times"] += prune_nones_list(data)

    if n_times == 1:
        times["times"] = times["times"][0]

    return times


def _read_oft(f, oft):
    """Read FOFT, COFT and GOFT blocks data."""
    history = {oft: []}

    while True:
        line = f.readline().rstrip()

        if line:
            history[oft].append(line)
        else:
            break

    return history


def _read_gener(f):
    """Read GENER block data."""
    gener = {"generators": {}}

    while True:
        line = f.readline()

        if line.strip():
            data = read_record(line, "5s,5s,5d,5d,5d,5d,5s,4s,1s,10e,10e,10e")
            label = data[0]
            tmp = {
                "name": [data[1]],
                "type": [data[7]],
                "layer_thickness": [data[11]],
            }

            ltab = data[5]
            if ltab and ltab > 1:
                for key in ["times", "rates", "specific_enthalpy"]:
                    table = []

                    while len(table) < ltab:
                        line = f.readline()
                        data = read_record(line, "14e,14e,14e,14e")
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


def _read_diffu(f):
    """Read DIFFU block data."""
    diffu = {"diffusion": []}

    for _ in range(2):
        line = f.readline()
        data = read_record(line, "10e,10e,10e,10e,10e,10e,10e,10e")
        diffu["diffusion"].append(prune_nones_list(data))

    return diffu


def _read_outpu(f):
    """Read OUTPU block data."""
    outpu = {"output": {}}

    # Format
    line = f.readline().strip()
    if line and not line.isdigit():
        outpu["output"]["format"] = line if line else None
        line = f.readline().strip()

    # Variables
    if line.isdigit():
        n_var = int(line)
        outpu["output"]["variables"] = {}

        for _ in range(n_var):
            line = f.readline()
            data = read_record(line, "20s,5d,5d")
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
