from __future__ import division, with_statement

import logging
from copy import deepcopy

import numpy as np

from ...._common import block_to_format, str2format
from ._common import default
from ._helpers import block, check_parameters, dtypes, write_record

__all__ = [
    "write",
]


def write(filename, parameters, block="all"):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str
        Output file name.
    parameters : dict
        Parameters to export.
    block : str {'all', 'gener', 'mesh', 'incon'}, optional, default 'all'
        Blocks to be written:
         - 'all': write all blocks,
         - 'gener': only write block GENER,
         - 'mesh': only write blocks ELEME, COORD and CONNE,
         - 'incon': only write block INCON.

    """
    buffer = write_buffer(parameters, block)
    with open(filename, "w") as f:
        for record in buffer:
            f.write(record)


@check_parameters(dtypes["PARAMETERS"])
def write_buffer(params, block):
    """Write TOUGH input file as a list of 80-character long record strings."""
    from ._common import Parameters, default, eos

    # Some preprocessing
    if block not in {"all", "gener", "mesh", "incon"}:
        raise ValueError()

    parameters = deepcopy(Parameters)
    parameters.update(deepcopy(params))

    parameters["title"] = (
        [parameters["title"]]
        if isinstance(parameters["title"], str)
        else parameters["title"]
    )

    for k, v in default.items():
        if k not in parameters["default"].keys():
            parameters["default"][k] = v

    for rock in parameters["rocks"].keys():
        for k, v in parameters["default"].items():
            cond1 = k not in parameters["rocks"][rock].keys()
            cond2 = k not in {
                "initial_condition",
                "relative_permeability",
                "capillarity",
            }
            if cond1 and cond2:
                parameters["rocks"][rock][k] = v

    # Make sure that some keys are integers and not strings
    if "more_options" in parameters:
        parameters["more_options"] = {
            int(k): v for k, v in parameters["more_options"].items()
        }
    if "extra_options" in parameters:
        parameters["extra_options"] = {
            int(k): v for k, v in parameters["extra_options"].items()
        }
    if "selections" in parameters and "integers" in parameters["selections"]:
        parameters["selections"]["integers"] = {
            int(k): v for k, v in parameters["selections"]["integers"].items()
        }

    # Check that EOS is defined (for block MULTI)
    if parameters["eos"] and parameters["eos"] not in eos.keys():
        raise ValueError(
            "EOS '{}' is unknown or not supported.".format(parameters["eos"])
        )

    # Set some flags
    cond1 = (
        "relative_permeability" in parameters["default"].keys()
        and parameters["default"]["relative_permeability"]["id"] is not None
    )
    cond2 = (
        "capillarity" in parameters["default"].keys()
        and parameters["default"]["capillarity"]["id"] is not None
    )
    rpcap = cond1 or cond2

    indom = False
    for rock in parameters["rocks"].values():
        if "initial_condition" in rock.keys():
            if any(x is not None for x in rock["initial_condition"][:4]):
                indom = True
                break

    multi = parameters["eos"] or (parameters["n_component"] and parameters["n_phase"])

    # Check that start is True if indom is True
    if indom and not parameters["start"]:
        logging.warning("Option 'START' is needed to use 'INDOM' conditions.")

    # Define input file contents
    out = []
    if block == "all":
        out += ["{:80}\n".format(title) for title in parameters["title"]]
        out += _write_rocks(parameters)
        out += _write_rpcap(parameters) if rpcap else []
        out += _write_flac(parameters) if parameters["flac"] is not None else []
        out += (
            _write_chemp(parameters)
            if parameters["chemical_properties"] is not None
            else []
        )
        out += (
            _write_ncgas(parameters)
            if parameters["non_condensible_gas"] is not None
            else []
        )
        out += _write_multi(parameters) if multi else []
        out += _write_solvr(parameters) if parameters["solver"] else []
        out += _write_start() if parameters["start"] else []
        out += _write_param(parameters)
        out += _write_selec(parameters) if parameters["selections"] else []
        out += _write_indom(parameters) if indom else []
        out += _write_momop(parameters) if parameters["more_options"] else []
        out += _write_times(parameters) if parameters["times"] is not None else []
        out += (
            _write_foft(parameters) if parameters["element_history"] is not None else []
        )
        out += (
            _write_coft(parameters)
            if parameters["connection_history"] is not None
            else []
        )
        out += (
            _write_goft(parameters)
            if parameters["generator_history"] is not None
            else []
        )

    if block in {"all", "gener"}:
        out += _write_gener(parameters) if parameters["generators"] else []

    if block == "all":
        out += _write_diffu(parameters) if parameters["diffusion"] is not None else []
        out += _write_outpu(parameters) if parameters["output"] else []

    if block in {"all", "mesh"}:
        out += _write_eleme(parameters) if parameters["elements"] else []
        out += _write_coord(parameters) if parameters["coordinates"] else []
        out += _write_conne(parameters) if parameters["connections"] else []

    if block in {"all", "incon"}:
        out += _write_incon(parameters) if parameters["initial_conditions"] else []

    if block == "all":
        out += _write_nover() if parameters["nover"] else []
        out += _write_endcy()

    return out


@check_parameters(dtypes["ROCKS"], keys="default")
@check_parameters(dtypes["ROCKS"], keys="rocks", is_list=True)
@check_parameters(
    dtypes["MODEL"], keys=("rocks", "relative_permeability"), is_list=True
)
@check_parameters(dtypes["MODEL"], keys=("rocks", "capillarity"), is_list=True)
@block("ROCKS", multi=True)
def _write_rocks(parameters):
    """Write ROCKS block data."""
    # Reorder rocks
    if parameters["rocks_order"] is not None:
        order = parameters["rocks_order"]
        for rock in parameters["rocks"].keys():
            if rock not in order:
                order.append(rock)
    else:
        order = parameters["rocks"].keys()

    # Formats
    fmt = block_to_format["ROCKS"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])

    fmt = block_to_format["RPCAP"]
    fmt3 = str2format(fmt)

    out = []
    for k in order:
        # Load data
        data = parameters["rocks"][k]

        # Number of additional lines to write per rock
        cond = any(
            data[k] is not None
            for k in [
                "compressibility",
                "expansivity",
                "conductivity_dry",
                "tortuosity",
                "klinkenberg_parameter",
                "distribution_coefficient_3",
                "distribution_coefficient_4",
            ]
        )
        nad = (
            2
            if "relative_permeability" in data.keys() or "capillarity" in data.keys()
            else int(cond)
        )

        # Permeability
        per = data["permeability"]
        per = [per] * 3 if not np.ndim(per) else per
        if not (isinstance(per, (list, tuple, np.ndarray)) and len(per) == 3):
            raise TypeError()

        # Record 1
        values = [
            k,
            nad if nad else "",
            data["density"],
            data["porosity"],
            per[0],
            per[1],
            per[2],
            data["conductivity"],
            data["specific_heat"],
        ]
        out += write_record(values, fmt1)

        # Record 2
        if cond:
            values = [
                data["compressibility"],
                data["expansivity"],
                data["conductivity_dry"],
                data["tortuosity"],
                data["klinkenberg_parameter"],
                data["distribution_coefficient_3"],
                data["distribution_coefficient_4"],
            ]
            out += write_record(values, fmt2)
        else:
            out += write_record([], []) if nad == 2 else []

        # Relative permeability / Capillary pressure
        if nad == 2:
            for key in ["relative_permeability", "capillarity"]:
                if key in data.keys():
                    values = [data[key]["id"], None]
                    values += list(data[key]["parameters"])
                    out += write_record(values, fmt3)
                else:
                    out += write_record([], [])

    return out


@check_parameters(dtypes["MODEL"], keys=("default", "relative_permeability"))
@check_parameters(dtypes["MODEL"], keys=("default", "capillarity"))
@block("RPCAP")
def _write_rpcap(parameters):
    """Write RPCAP block data."""
    data = deepcopy(default)
    data.update(parameters["default"])

    # Formats
    fmt = block_to_format["RPCAP"]
    fmt = str2format(fmt)

    out = []
    for key in ["relative_permeability", "capillarity"]:
        if key in data.keys():
            values = [data[key]["id"], None]
            values += list(data[key]["parameters"])
            out += write_record(values, fmt)
        else:
            out += write_record([], [])

    return out


@check_parameters(dtypes["FLAC"], keys="flac")
@check_parameters(dtypes["MODEL"], keys=("default", "permeability_model"))
@check_parameters(dtypes["MODEL"], keys=("default", "equivalent_pore_pressure"))
@check_parameters(dtypes["MODEL"], keys=("rocks", "permeability_model"), is_list=True)
@check_parameters(
    dtypes["MODEL"], keys=("rocks", "equivalent_pore_pressure"), is_list=True
)
@block("FLAC", multi=True)
def _write_flac(parameters):
    """Write FLAC block data."""
    # Load data
    from ._common import flac

    data = deepcopy(flac)
    data.update(parameters["flac"])

    # Reorder rocks
    if parameters["rocks_order"]:
        order = parameters["rocks_order"]
        for rock in parameters["rocks"].keys():
            if rock not in order:
                order.append(rock)
    else:
        order = parameters["rocks"].keys()

    # Formats
    fmt = block_to_format["FLAC"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])
    fmt3 = str2format(fmt[3])

    # Record 1
    values = [
        bool(data["creep"]),
        data["porosity_model"],
        data["version"],
    ]
    out = write_record(values, fmt1)

    # Additional records
    for k in order:
        # Load data
        data = deepcopy(default)
        data.update(parameters["default"])
        data.update(parameters["rocks"][k])

        # Permeability model
        values = [data["permeability_model"]["id"]]
        values += list(data["permeability_model"]["parameters"])
        out += write_record(values, fmt2)

        # Equivalent pore pressure
        values = [data["equivalent_pore_pressure"]["id"], None]
        values += list(data["equivalent_pore_pressure"]["parameters"])
        out += write_record(values, fmt3)

    return out


@check_parameters(dtypes["CHEMP"], keys="chemical_properties", is_list=True)
@block("CHEMP")
def _write_chemp(parameters):
    """Write CHEMP block data."""
    # Load data
    from ._common import chemical_properties

    data = parameters["chemical_properties"]

    # Formats
    fmt = block_to_format["CHEMP"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])
    fmt3 = str2format(fmt[3])

    # Record 1
    out = write_record([len(data)], fmt1)

    # Record 2
    for k, v in data.items():
        vv = deepcopy(chemical_properties)
        vv.update(v)

        out += write_record([k], fmt2)

        values = [
            vv["temperature_crit"],
            vv["pressure_crit"],
            vv["compressibility_crit"],
            vv["pitzer_factor"],
            vv["dipole_moment"],
        ]
        out += write_record(values, fmt3)

        values = [
            vv["boiling_point"],
            vv["vapor_pressure_a"],
            vv["vapor_pressure_b"],
            vv["vapor_pressure_c"],
            vv["vapor_pressure_d"],
        ]
        out += write_record(values, fmt3)

        values = [
            vv["molecular_weight"],
            vv["heat_capacity_a"],
            vv["heat_capacity_b"],
            vv["heat_capacity_c"],
            vv["heat_capacity_d"],
        ]
        out += write_record(values, fmt3)

        values = [
            vv["napl_density_ref"],
            vv["napl_temperature_ref"],
            vv["gas_diffusivity_ref"],
            vv["gas_temperature_ref"],
            vv["exponent"],
        ]
        out += write_record(values, fmt3)

        values = [
            vv["napl_viscosity_a"],
            vv["napl_viscosity_b"],
            vv["napl_viscosity_c"],
            vv["napl_viscosity_d"],
            vv["volume_crit"],
        ]
        out += write_record(values, fmt3)

        values = [
            vv["solubility_a"],
            vv["solubility_b"],
            vv["solubility_c"],
            vv["solubility_d"],
        ]
        out += write_record(values, fmt3)

        values = [
            vv["oc_coeff"],
            vv["oc_fraction"],
            vv["oc_decay"],
        ]
        out += write_record(values, fmt3)

    return out


@block("NCGAS")
def _write_ncgas(parameters):
    """Write NCGAS block data."""
    data = parameters["non_condensible_gas"]

    # Formats
    fmt = block_to_format["NCGAS"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])

    # Record 1
    out = write_record([len(data)], fmt1)

    # Record 2
    out += write_record(data, fmt2, multi=True)

    return out


@block("MULTI")
def _write_multi(parameters):
    """Write MULTI block data."""
    from ._common import eos

    if "eos" in parameters and parameters["eos"] == "tmvoc":
        for keyword in {"n_component", "n_phase"}:
            if parameters[keyword] is None:
                raise ValueError(
                    "for 'tmvoc', at least 'n_component' and 'n_phase' must be specified"
                )

    # Formats
    fmt = block_to_format["MULTI"]
    fmt = str2format(fmt)

    values = (
        list(eos[parameters["eos"]])
        if parameters["eos"] and parameters["eos"] != "tmvoc"
        else [0, 0, 0, 6]
    )
    values[0] = parameters["n_component"] if parameters["n_component"] else values[0]
    values[1] = values[0] if parameters["isothermal"] else values[0] + 1
    values[2] = parameters["n_phase"] if parameters["n_phase"] else values[2]

    # Handle diffusion
    if parameters["diffusion"]:
        values[3] = 8
        parameters["n_phase"] = values[2]  # Save for later check

    # Number of mass components
    if parameters["n_component_incon"]:
        values.append(parameters["n_component_incon"])

    out = write_record(values, fmt)

    return out


@check_parameters(dtypes["SOLVR"], keys="solver")
@block("SOLVR")
def _write_solvr(parameters):
    """Write SOLVR block data."""
    from ._common import solver

    data = deepcopy(solver)
    data.update(parameters["solver"])

    # Formats
    fmt = block_to_format["SOLVR"]
    fmt = str2format(fmt)

    values = [
        data["method"],
        None,
        data["z_precond"],
        None,
        data["o_precond"],
        data["rel_iter_max"],
        data["eps"],
    ]
    out = write_record(values, fmt)

    return out


@block("START")
def _write_start():
    """Write START block data."""
    from ._common import header

    out = "{:5}{}\n".format("----*", header)
    return [out[:11] + "MOP: 123456789*123456789*1234" + out[40:]]


@check_parameters(dtypes["PARAM"], keys="options")
@check_parameters(dtypes["MOP"], keys="extra_options")
@block("PARAM")
def _write_param(parameters):
    """Write PARAM block data."""
    # Load data
    from ._common import extra_options, options

    data = deepcopy(options)
    data.update(parameters["options"])

    # Table
    if not isinstance(data["t_steps"], (list, tuple, np.ndarray)):
        data["t_steps"] = [data["t_steps"]]

    # Formats
    fmt = block_to_format["PARAM"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])
    fmt3 = str2format(fmt[3])
    fmt4 = str2format(fmt[4])
    fmt5 = str2format(fmt[5])

    # Record 1
    _mop = deepcopy(extra_options)
    _mop.update(parameters["extra_options"])
    mop = [" " if _mop[k] is None else str(_mop[k]) for k in sorted(_mop.keys())]

    values = [
        data["n_iteration"],
        data["verbosity"],
        data["n_cycle"],
        data["n_second"],
        data["n_cycle_print"],
        "{}".format("".join(mop)),
        None,
        data["temperature_dependence_gas"],
        data["effective_strength_vapor"],
    ]
    out = write_record(values, fmt1)

    # Record 2
    values = [
        data["t_ini"],
        data["t_max"],
        -((len(data["t_steps"]) - 1) // 8 + 1),
        data["t_step_max"],
        None,
        data["gravity"],
        data["t_reduce_factor"],
        data["mesh_scale_factor"],
    ]
    out += write_record(values, fmt2)

    # Record 2.1
    values = [x for x in data["t_steps"]]
    out += write_record(values, fmt3, multi=True)

    # Record 3
    values = [
        data["eps1"],
        data["eps2"],
        None,
        data["w_upstream"],
        data["w_newton"],
        data["derivative_factor"],
    ]
    out += write_record(values, fmt4)

    # Record 4
    n = min(4, len(parameters["default"]["initial_condition"]))
    values = parameters["default"]["initial_condition"][:n]
    out += write_record(values, fmt5)

    # Record 5 (EOS7R)
    if len(parameters["default"]["initial_condition"]) > 4:
        values = parameters["default"]["initial_condition"][n:]
        out += write_record(values, fmt5)

    return out


@check_parameters(dtypes["SELEC"], keys="selections")
@block("SELEC")
def _write_selec(parameters):
    """Write SELEC block data."""
    # Load data
    from ._common import selections

    data = deepcopy(selections)
    if parameters["selections"]["integers"]:
        data["integers"].update(parameters["selections"]["integers"])
    if "floats" in parameters["selections"] and len(parameters["selections"]["floats"]):
        data["floats"] = parameters["selections"]["floats"]

    # Check floats and overwrite IE(1)
    if data["floats"] is not None and len(data["floats"]):
        if isinstance(data["floats"][0], (list, tuple, np.ndarray)):
            for x in data["floats"]:
                if len(x) > 8:
                    raise ValueError()

            data["integers"][1] = len(data["floats"])
            ndim = 2

        else:
            if len(data["floats"]) > 8:
                raise ValueError()

            data["integers"][1] = 1
            ndim = 1
    else:
        ndim = None

    # Formats
    fmt = block_to_format["SELEC"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])

    # Record 1
    values = [data["integers"][k] for k in sorted(data["integers"].keys())]
    out = write_record(values, fmt1)

    # Record 2
    if ndim == 1:
        out += write_record(data["floats"], fmt2)
    elif ndim == 2:
        for x in data["floats"]:
            out += write_record(x, fmt2)

    return out


@block("INDOM", multi=True)
def _write_indom(parameters):
    """Write INDOM block data."""
    if parameters["rocks_order"]:
        order = parameters["rocks_order"]
        for rock in parameters["rocks"].keys():
            if rock not in order:
                order.append(rock)
    else:
        order = parameters["rocks"].keys()

    # Formats
    fmt = block_to_format["INDOM"]
    fmt1 = str2format(fmt[5])
    fmt2 = str2format(fmt[0])

    out = []
    for k in order:
        if "initial_condition" in parameters["rocks"][k]:
            data = parameters["rocks"][k]["initial_condition"]
            if any(x is not None for x in data):
                # Record 1
                values = [k]
                out += write_record(values, fmt1)

                # Record 2
                n = min(4, len(data))
                values = list(data[:n])
                out += write_record(values, fmt2)

                # Record 3
                if len(data) > 4:
                    values = list(data[4:])
                    out += write_record(values, fmt2)

    return out


@check_parameters(dtypes["MOMOP"], keys="more_options")
@block("MOMOP")
def _write_momop(parameters):
    """Write MOMOP block data."""
    from ._common import more_options

    # Formats
    fmt = block_to_format["MOMOP"]
    fmt = str2format(fmt)

    _momop = deepcopy(more_options)
    _momop.update(parameters["more_options"])

    tmp = [" " if _momop[k] is None else str(_momop[k]) for k in sorted(_momop.keys())]
    out = write_record(["".join(tmp)], fmt)

    return out


@block("TIMES")
def _write_times(parameters):
    """Write TIMES block data."""
    data = parameters["times"]
    data = data if np.ndim(data) else [data]

    # Formats
    fmt = block_to_format["TIMES"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])

    # Record 1
    out = write_record([len(data)], fmt1)

    # Record 2
    out += write_record(data, fmt2, multi=True)

    return out


@block("FOFT", multi=True)
def _write_foft(parameters):
    """Write FOFT block data."""
    # Formats
    fmt = block_to_format["FOFT"]
    fmt = str2format(fmt[5])

    values = [x for x in parameters["element_history"]]
    out = write_record(values, fmt, multi=True)

    return out


@block("COFT", multi=True)
def _write_coft(parameters):
    """Write COFT block data."""
    # Format
    fmt = block_to_format["COFT"]
    fmt = str2format(fmt[5])

    values = [x for x in parameters["connection_history"]]
    out = write_record(values, fmt, multi=True)

    return out


@block("GOFT", multi=True)
def _write_goft(parameters):
    """Write GOFT block data."""
    # Format
    fmt = block_to_format["GOFT"]
    fmt = str2format(fmt[5])

    values = [x for x in parameters["generator_history"]]
    out = write_record(values, fmt, multi=True)

    return out


@check_parameters(dtypes["GENER"], keys="generators", is_list=True)
@block("GENER", multi=True)
def _write_gener(parameters):
    """Write GENER block data."""
    from ._common import generators

    # Handle multicomponent generators
    generator_data = []
    keys = [key for key in generators.keys() if key != "type"]
    for k, v in parameters["generators"].items():
        # Load data
        data = deepcopy(generators)
        data.update(v)

        # Check that data are consistent
        if not isinstance(data["type"], str):
            # Number of components
            num_comps = len(data["type"])

            # Check that values in dict have the same length
            for key in keys:
                if data[key] is not None:
                    if not isinstance(data[key], (list, tuple, np.ndarray)):
                        raise TypeError()
                    if len(data[key]) != num_comps:
                        raise ValueError()

            # Split dict
            for i in range(num_comps):
                generator_data.append(
                    (
                        k,
                        {
                            key: (data[key][i] if data[key] is not None else None)
                            for key in generators.keys()
                        },
                    )
                )
        else:
            # Only one component for this element
            # Check that values are scalar or 1D array_like
            for key in keys:
                if np.ndim(data[key]) not in {0, 1}:
                    raise ValueError()
            generator_data.append((k, data))

    # Format
    label_length = max(len(max(parameters["generators"], key=len)), 5)
    fmt = block_to_format["GENER"]
    fmt1 = str2format(fmt[label_length])
    fmt2 = str2format(fmt[0])

    out = []
    for k, v in generator_data:
        # Table
        ltab = None
        if v["times"] is not None and isinstance(v["times"], (list, tuple, np.ndarray)):
            ltab = len(v["times"])
            for key in ["rates", "specific_enthalpy"]:
                if v[key] is not None:
                    if not isinstance(v[key], (list, tuple, np.ndarray)):
                        raise TypeError()
                    if not (ltab > 1 and ltab == len(v[key])):
                        raise ValueError()
        else:
            # Rates and specific enthalpy tables cannot be written without a
            # time table
            for key in ["rates", "specific_enthalpy"]:
                if v[key] is not None and np.ndim(v[key]) != 0:
                    raise ValueError()

        itab = (
            1 if isinstance(v["specific_enthalpy"], (list, tuple, np.ndarray)) else None
        )

        # Record 1
        values = [
            k,
            v["name"],
            v["nseq"],
            v["nadd"],
            v["nads"],
            ltab,
            None,
            v["type"],
            itab,
            None if ltab else v["rates"],
            None if ltab else v["specific_enthalpy"],
            v["layer_thickness"],
        ]
        out += write_record(values, fmt1)

        # Record 2
        out += write_record(v["times"], fmt2, multi=True) if ltab else []

        # Record 3
        out += write_record(v["rates"], fmt2, multi=True) if ltab else []

        # Record 4
        if ltab and v["specific_enthalpy"] is not None:
            if isinstance(v["specific_enthalpy"], (list, tuple, np.ndarray)):
                specific_enthalpy = v["specific_enthalpy"]
            else:
                specific_enthalpy = np.full(ltab, v["specific_enthalpy"])

            out += write_record(specific_enthalpy, fmt2, multi=True)

    return out


@block("DIFFU")
def _write_diffu(parameters):
    """Write DIFFU block data."""
    # Format
    fmt = block_to_format["DIFFU"]
    fmt = str2format(fmt)

    out = []
    for mass in parameters["diffusion"]:
        out += write_record(mass, fmt, multi=True)

    return out


@check_parameters(dtypes["OUTPU"], keys="output")
@block("OUTPU")
def _write_outpu(parameters):
    """Write OUTPU block data."""
    # Load data
    from ._common import output

    data = deepcopy(output)
    data.update(parameters["output"])

    # Format
    fmt = block_to_format["OUTPU"]
    fmt1 = str2format(fmt[1])
    fmt2 = str2format(fmt[2])
    fmt3 = str2format(fmt[3])

    out = []

    # Output format
    out += write_record([data["format"].upper()], fmt1) if data["format"] else []

    # Variables
    if data["variables"]:
        buffer = []
        num_vars = 0
        for k, v in data["variables"].items():
            values = [k.upper()]

            if np.ndim(v) == 0:
                values += [v]
                buffer += write_record(values, fmt3)
                num_vars += 1
            else:
                if np.ndim(v[0]) == 0:
                    values += list(v)
                    buffer += write_record(values, fmt3)
                    num_vars += 1
                else:
                    for vv in v:
                        values_in = values + list(vv)
                        buffer += write_record(values_in, fmt3)
                    num_vars += len(v)

        out += write_record([str(num_vars)], fmt2)
        out += buffer

    return out


@check_parameters(dtypes["ELEME"], keys="elements", is_list=True)
@block("ELEME", multi=True)
def _write_eleme(parameters):
    """Write ELEME block data."""
    from ._common import elements

    # Reorder elements
    if parameters["elements_order"] is not None:
        order = parameters["elements_order"]
    else:
        order = parameters["elements"].keys()

    # Format
    label_length = len(max(parameters["elements"], key=len))
    fmt = block_to_format["ELEME"]
    fmt = str2format(fmt[label_length])

    out = []
    for k in order:
        data = deepcopy(elements)
        data.update(parameters["elements"][k])

        material = (
            "{:>5}".format(data["material"])
            if isinstance(data["material"], int)
            else data["material"]
        )
        values = [
            k,
            data["nseq"],
            data["nadd"],
            material,
            data["volume"],
            data["heat_exchange_area"],
            data["permeability_modifier"],
            data["center"][0],
            data["center"][1],
            data["center"][2],
        ]
        out += write_record(values, fmt)

    return out


@block("COORD", multi=True)
def _write_coord(parameters):
    """Write COORD block data."""
    # Reorder elements
    if parameters["elements_order"] is not None:
        order = parameters["elements_order"]
    else:
        order = parameters["elements"].keys()

    # Format
    fmt = block_to_format["COORD"]
    fmt = str2format(fmt)

    out = []
    for k in order:
        values = parameters["elements"][k]["center"]
        out += write_record(values, fmt)

    return out


@check_parameters(dtypes["CONNE"], keys="connections", is_list=True)
@block("CONNE", multi=True)
def _write_conne(parameters):
    """Write CONNE block data."""
    from ._common import connections

    # Reorder connections
    if parameters["connections_order"] is not None:
        order = parameters["connections_order"]
    else:
        order = parameters["connections"].keys()

    # Format
    label_length = len(max(parameters["connections"], key=len)) // 2
    fmt = block_to_format["CONNE"]
    fmt = str2format(fmt[label_length])

    out = []
    for k in order:
        data = deepcopy(connections)
        data.update(parameters["connections"][k])

        values = [
            k,
            data["nseq"],
            data["nadd"][0] if data["nadd"] is not None else None,
            data["nadd"][1] if data["nadd"] is not None else None,
            data["permeability_direction"],
            data["nodal_distances"][0],
            data["nodal_distances"][1],
            data["interface_area"],
            data["gravity_cosine_angle"],
            data["radiant_emittance_factor"],
        ]
        out += write_record(values, fmt)

    return out


@check_parameters(dtypes["INCON"], keys="initial_conditions", is_list=True)
@block("INCON", multi=True)
def _write_incon(parameters):
    """Write INCON block data."""
    from ._common import initial_conditions

    # Reorder connections
    if parameters["initial_conditions_order"] is not None:
        order = parameters["initial_conditions_order"]
    else:
        order = parameters["initial_conditions"].keys()

    # Format
    label_length = len(max(parameters["initial_conditions"], key=len))
    fmt = block_to_format["INCON"]
    fmt1 = str2format(fmt[label_length])
    fmt2 = str2format(fmt[0])

    out = []
    for k in order:
        data = deepcopy(initial_conditions)
        data.update(parameters["initial_conditions"][k])

        # Record 1
        values = [
            k,
            None,
            None,
            data["porosity"],
        ]
        values += list(data["userx"])
        out += write_record(values, fmt1)

        # Record 2
        n = min(4, len(data["values"]))
        out += write_record(data["values"][:n], fmt2)

        # Record 3 (EOS7R)
        if len(data["values"]) > 4:
            out += write_record(data["values"][4:], fmt2)

    return out


@block("NOVER")
def _write_nover():
    """Write NOVER block data."""
    return []


@block("ENDCY", noend=True)
def _write_endcy():
    """Write ENDCY block data."""
    return []
