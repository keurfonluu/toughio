import logging

import numpy as np

from .._common import to_str
from ...._common import open_file

__all__ = [
    "write",
]


def write(filename, parameters, mopr_11=0, verbose=True):
    buffer = write_buffer(parameters, mopr_11, verbose)
    with open_file(filename, "w") as f:
        for record in buffer:
            f.write(record)


def write_buffer(parameters, mopr_11=0, verbose=True):
    numbers = _generate_numbers(parameters)

    # Define input file contents
    out = []
    out += _write_title(parameters, verbose)
    out += _write_options(parameters, verbose)
    out += _write_filenames(parameters, verbose)
    out += _write_weights_coefficients(parameters, verbose)
    out += _write_convergence(parameters, verbose)
    out += _write_output(parameters, numbers, verbose)
    
    if numbers["NWNOD"]:
        out += _write_elements(parameters, verbose)

    if numbers["NWCOM"]:
        out += _write_indices_names(parameters, "components", numbers["NWCOM"], verbose)

    if numbers["NWMIN"]:
        out += _write_indices_names(parameters, "minerals", numbers["NWMIN"], verbose)

    if numbers["NWAQ"]:
        out += _write_indices_names(parameters, "aqueous_species", numbers["NWAQ"], verbose)

    if numbers["NWADS"]:
        out += _write_indices_names(parameters, "surface_complexes", numbers["NWADS"], verbose)

    if numbers["NWEXC"]:
        out += _write_indices_names(parameters, "exchange_species", numbers["NWEXC"], verbose)

    out += _write_default(parameters, verbose, mopr_11)

    return out


def _generate_numbers(parameters):
    numbers = {
        "NWNOD": -len(_get(parameters, ("output", "elements"), [])),
        "NWCOM": len(_get(parameters, ("output", "components"), [])),
        "NWMIN": len(_get(parameters, ("output", "minerals"), [])),
        "NWAQ": len(_get(parameters, ("output", "aqueous_species"), [])),
        "NWADS": len(_get(parameters, ("output", "surface_complexes"), [])),
        "NWEXC": len(_get(parameters, ("output", "exchange_species"), [])),
    }

    if numbers["NWCOM"]:
        if isinstance(parameters["output"]["components"][0], str):
            numbers["NWNOD"] *= -1

    if numbers["NWMIN"]:
        if isinstance(parameters["output"]["minerals"][0], str):
            numbers["NWMIN"] *= -1

    if numbers["NWAQ"]:
        if isinstance(parameters["output"]["aqueous_species"][0], str):
            numbers["NWAQ"] *= -1

    if numbers["NWADS"]:
        if isinstance(parameters["output"]["surface_complexes"][0], str):
            numbers["NWADS"] *= -1

    if numbers["NWEXC"]:
        if isinstance(parameters["output"]["exchange_species"][0], str):
            numbers["NWEXC"] *= -1

    return numbers


def _write_title(parameters, verbose):
    out = []
    out += ["# Title\n"] if verbose else []
    out += [f"{parameters['title']}\n"]

    return out


def _write_options(parameters, verbose):
    out = []

    # Record 2
    values = [
        _get(parameters, ("flags", "iteration_scheme"), 0),
        _get(parameters, ("flags", "reactive_surface_area"), 0),
        _get(parameters, ("flags", "solver"), 0),
        _get(parameters, ("flags", "n_subiteration"), 0),
        _get(parameters, ("flags", "gas_transport"), 0),
        _get(parameters, ("flags", "verbosity"), 0),
        _get(parameters, ("flags", "feedback"), 0),
        _get(parameters, ("flags", "coupling"), 0),
        0,
    ]

    if verbose:
        out += ["# ISPIA ITERSFA  ISOLVC   NGAMM   NGAS1 ICHDUMP    KCPL ICO2H2O iTDS_REACT\n"]
        out += "{}\n".format(
            " ".join(
                [
                    to_str(values[0], "{:7d}"),
                    to_str(values[1], "{:7d}"),
                    to_str(values[2], "{:7d}"),
                    to_str(values[3], "{:7d}"),
                    to_str(values[4], "{:7d}"),
                    to_str(values[5], "{:7d}"),
                    to_str(values[6], "{:7d}"),
                    to_str(values[7], "{:7d}"),
                    to_str(values[8], "{:10d}"),
                ]
            )
        )

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    # Record 3
    values = [
        _get(parameters, ("options", "sl_min"), 0.0),
        _get(parameters, ("options", "rcour"), 0.0),
        _get(parameters, ("options", "ionic_strength_max"), 0.0),
        _get(parameters, ("options", "mineral_gas_factor"), 0.0),
    ]

    if verbose:
        out += ["#   SL1MIN     RCOUR    STIMAX    CNFACT\n"]
        out += " {}\n".format(
            " ".join(
                [
                    to_str(values[0], "{{:9f}}"),
                    to_str(values[1], "{{:9f}}"),
                    to_str(values[2], "{{:9f}}"),
                    to_str(values[3], "{{:9f}}"),
                ]
            )
        )

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_filenames(parameters, verbose):
    out = []
    values = [
        _get(parameters, ("files", "thermodynamic_input"), ""),
        _get(parameters, ("files", "iteration_output"), ""),
        _get(parameters, ("files", "plot_output"), ""),
        _get(parameters, ("files", "solid_output"), ""),
        _get(parameters, ("files", "gas_output"), ""),
        _get(parameters, ("files", "time_output"), ""),
    ]

    if verbose:
        out += ["# Input and output file names\n"]
        out += [f"{values[0]:<20}  ! Thermodynamic database\n"]
        out += [f"{values[1]:<20}  ! Iteration information\n"]
        out += [f"{values[2]:<20}  ! Aqueous concentrations in Tecplot form\n"]
        out += [f"{values[3]:<20}  ! Mineral data in Tecplot form\n"]
        out += [f"{values[4]:<20}  ! Gas data in Tecplot form\n"]
        out += [f"{values[5]:<20}  ! Concentrations at specific elements over time\n"]

    else:
        out += [f"{value}\n" for value in values]

    return out


def _write_weights_coefficients(parameters, verbose):
    out = []
    values = [
        _get(parameters, ("options", "w_time"), 0.0),
        _get(parameters, ("options", "w_upstream"), 0.0),
        _get(parameters, ("options", "aqueous_diffusion_coefficient"), 0.0),
        _get(parameters, ("options", "molecular_diffusion_coefficient"), 0.0),
    ]

    if verbose:
        out += ["#    ITIME      WUPC     DFFUN    DFFUNG\n"]
        out += " {}\n".format(
            " ".join(
                [
                    to_str(values[0], "{{:9f}}"),
                    to_str(values[1], "{{:9f}}"),
                    to_str(values[2], "{{:9f}}"),
                    to_str(values[3], "{{:9f}}"),
                ]
            )
        )

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_convergence(parameters, verbose):
    out = []
    values = [
        _get(parameters, ("options", "n_iteration_tr"), 0),
        _get(parameters, ("options", "eps_tr"), 0.0),
        _get(parameters, ("options", "n_iteration_ch"), 0),
        _get(parameters, ("options", "eps_ch"), 0.0),
        _get(parameters, ("options", "eps_mb"), 0.0),
        _get(parameters, ("options", "eps_dc"), 0.0),
        _get(parameters, ("options", "eps_dr"), 0.0),
    ]

    if verbose:
        out += ["# MAXITPTR     TOLTR  MAXITPCH     TOLCH     TOLMB     TOLDC     TOLDR\n"]
        out += " {}\n".format(
            " ".join(
                [
                    to_str(values[0], "{:9d}"),
                    to_str(values[1], "{{:9f}}"),
                    to_str(values[2], "{:9d}"),
                    to_str(values[3], "{{:9f}}"),
                    to_str(values[4], "{{:9f}}"),
                    to_str(values[5], "{{:9f}}"),
                    to_str(values[6], "{{:9f}}"),
                ]
            )
        )

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_output(parameters, numbers, verbose):
    out = []
    values = [
        _get(parameters, ("options", "n_cycle_print"), 0),
        numbers["NWNOD"],
        numbers["NWCOM"],
        numbers["NWMIN"],
        numbers["NWAQ"],
        numbers["NWADS"],
        numbers["NWEXC"],
        _get(parameters, ("flags", "aqueous_concentration_unit"), 0),
        _get(parameters, ("flags", "mineral_unit"), 0),
        _get(parameters, ("flags", "gas_concentration_unit"), 0),
    ]

    if verbose:
        out += ["#  NWTI  NWNOD  NWCOM  NWMIN   NWAQ  NWADS  NWEXC   ICON    MIN   IGAS\n"]
        out += " {}\n".format(
            " ".join(
                [
                    to_str(values[0], "{:6d}"),
                    to_str(values[1], "{:6d}"),
                    to_str(values[2], "{:6d}"),
                    to_str(values[3], "{:6d}"),
                    to_str(values[4], "{:6d}"),
                    to_str(values[5], "{:6d}"),
                    to_str(values[6], "{:6d}"),
                    to_str(values[7], "{:6d}"),
                    to_str(values[8], "{:6d}"),
                    to_str(values[9], "{:6d}"),
                ]
            )
        )

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_elements(parameters, verbose):
    out = []
    out += [f"# {comments['nodes']}\n"] if verbose else []
    out += [f"{x[:5]}\n" for x in parameters["output"]["elements"]]
    out += ["\n"]

    return out


def _write_indices_names(parameters, key, n, verbose):
    out = []
    out += [f"# {comments[key]}\n"] if verbose else []

    if n > 0:
        out += f"{' '.join(str(x) for x in parameters['output'][key])}\n"

    else:
        out += [f"{x[:20]}\n" for x in parameters["output"][key]]
        out += ["\n"]

    return out


def _write_default(parameters, verbose, mopr_11=0):
    out = []
    values = [
        _get(parameters, ("default", "initial_water"), 0),
        _get(parameters, ("default", "injection_water"), 0),
        _get(parameters, ("default", "mineral"), 0),
        _get(parameters, ("default", "gas"), 0),
        _get(parameters, ("default", "adsorption"), 0),
        _get(parameters, ("default", "ion_exchange"), 0),
        _get(parameters, ("default", "porosity_permeability"), 0),
        _get(parameters, ("default", "linear_adsorption"), 0),
        _get(parameters, ("default", "injection_gas"), 0),
    ]

    if mopr_11 != 1:
        if "element" in parameters["default"]:
            values += [parameters["default"]["element"]]

    else:
        values += [_get(parameters, ("default", "sedimentation_velocity"), 0)]

    if verbose:
        out += [f"# IZIWDF IZBWDF IZMIDF IZGSDF IZADDF IZEXDF IZPPDF IZKDDF IZBGDF\n"]
        out += "  {}\n".format(" ".join(to_str(value, "{:6d}") for value in values))

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _get(parameters, keys, default):
    try:
        if isinstance(keys, str):
            return parameters[keys]

        else:
            value = parameters
            for key in keys:
                value = value[key]

            return value

    except KeyError:
        key_str = (
            "'{}'".format(keys)
            if isinstance(keys, str)
            else "".join(f"['{key}']" for key in keys)
        )
        logging.warning(f"Key {key_str} is not defined. Set to {default} by default.")

        return 
        

comments = {
    "nodes": "Nodes",
    "components": "Primary aqueous species",
    "minerals": "Minerals",
    "aqueous_species": "Individual aqueous species",
    "surface_complexes": "Adsorption species",
    "exchange_species": "Exchange species",
}
