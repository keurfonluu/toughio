import logging

from .._common import to_str
from ...._common import open_file

__all__ = [
    "write",
]


def write(filename, parameters, mopr_10=0, mopr_11=0, verbose=True):
    buffer = write_buffer(parameters, mopr_10, mopr_11, verbose)
    with open_file(filename, "w") as f:
        for record in buffer:
            f.write(record)


def write_buffer(parameters, mopr_10=0, mopr_11=0, verbose=True):
    numbers = _generate_numbers(parameters)

    # Define input file contents
    out = []
    out += _write_title(parameters, verbose)
    out += _write_options(parameters, verbose)
    out += _write_filenames(parameters, verbose)
    out += _write_weights_coefficients(parameters, verbose)
    out += _write_convergence(parameters, verbose)
    out += _write_output(parameters, numbers, verbose)
    out += _write_elements(parameters, numbers["NWNOD"], verbose)
    out += _write_indices_names(parameters, "components", numbers["NWCOM"], verbose)
    out += _write_indices_names(parameters, "minerals", numbers["NWMIN"], verbose)
    out += _write_indices_names(parameters, "aqueous_species", numbers["NWAQ"], verbose)
    out += _write_indices_names(parameters, "surface_complexes", numbers["NWADS"], verbose)
    out += _write_indices_names(parameters, "exchange_species", numbers["NWEXC"], verbose)
    out += _write_default(parameters, verbose, mopr_11)
    out += _write_zones(parameters, verbose, mopr_11)
    out += _write_convergence_bounds(parameters, verbose, mopr_10)
    out += ["end\n"]

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
    out = ["# Title\n"] if verbose else []
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
        out += " {}\n".format(" ".join(to_str(value, "{{:9f}}") for value in values))

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_filenames(parameters, verbose):
    out = ["# Input and output file names\n"] if verbose else []
    values = [
        _get(parameters, ("files", "thermodynamic_input"), ""),
        _get(parameters, ("files", "iteration_output"), ""),
        _get(parameters, ("files", "plot_output"), ""),
        _get(parameters, ("files", "solid_output"), ""),
        _get(parameters, ("files", "gas_output"), ""),
        _get(parameters, ("files", "time_output"), ""),
    ]

    if verbose:
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
    out = ["#    ITIME      WUPC     DFFUN    DFFUNG\n"] if verbose else []
    values = [
        _get(parameters, ("options", "w_time"), 0.0),
        _get(parameters, ("options", "w_upstream"), 0.0),
        _get(parameters, ("options", "aqueous_diffusion_coefficient"), 0.0),
        _get(parameters, ("options", "molecular_diffusion_coefficient"), 0.0),
    ]

    if verbose:
        out += " {}\n".format(" ".join(to_str(value, "{{:9f}}") for value in values))

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_convergence(parameters, verbose):
    out = ["# MAXITPTR     TOLTR  MAXITPCH     TOLCH     TOLMB     TOLDC     TOLDR\n"] if verbose else []
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
    out = ["#  NWTI  NWNOD  NWCOM  NWMIN   NWAQ  NWADS  NWEXC   ICON    MIN   IGAS\n"] if verbose else []
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
        out += " {}\n".format(" ".join(to_str(value, "{:6d}") for value in values))

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_elements(parameters, n, verbose):
    out = [f"# {comments['nodes']}\n"] if verbose else []

    if n == 0:
        out += ["\n"]

        return out
    
    out += [f"{x[:5]}\n" for x in parameters["output"]["elements"]]
    out += ["\n"]

    return out


def _write_indices_names(parameters, key, n, verbose):
    out = [f"# {comments[key]}\n"] if verbose else []

    if n == 0:
        out += ["\n"]

        return out

    if n > 0:
        out += f"{' '.join(str(x) for x in parameters['output'][key])}\n"

    else:
        out += [f"{x[:20]}\n" for x in parameters["output"][key]]
        out += ["\n"]

    return out


def _write_default(parameters, verbose, mopr_11=0):
    out = [f"#IZIWDF IZBWDF IZMIDF IZGSDF IZADDF IZEXDF IZPPDF IZKDDF IZBGDF\n"] if verbose else []
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
        out += " {}\n".format(" ".join(to_str(value, "{:6d}") for value in values))

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    return out


def _write_zones(parameters, verbose, mopr_11=0):
    out = ["#ELEM NSEQ NADD IZIW IZBW IZMI IZGS IZAD IZEX IZPP IZKD IZBG\n"] if verbose else []
    
    if not parameters["zones"]:
        out += ["\n"]

        return out
    
    # Do not use items() for better warning logging in function _get
    for zone in parameters["zones"]:
        values = [
            zone,
            _get(parameters, ("zones", zone, "nseq"), 0),
            _get(parameters, ("zones", zone, "nadd"), 0),
            _get(parameters, ("zones", zone, "initial_water"), 0),
            _get(parameters, ("zones", zone, "injection_water"), 0),
            _get(parameters, ("zones", zone, "mineral"), 0),
            _get(parameters, ("zones", zone, "gas"), 0),
            _get(parameters, ("zones", zone, "adsorption"), 0),
            _get(parameters, ("zones", zone, "ion_exchange"), 0),
            _get(parameters, ("zones", zone, "porosity_permeability"), 0),
            _get(parameters, ("zones", zone, "linear_adsorption"), 0),
            _get(parameters, ("zones", zone, "injection_gas"), 0),
        ]

        if mopr_11 != 1:
            if "element" in parameters["zones"][zone]:
                values += [parameters["zones"][zone]["element"]]

        else:
            values += [_get(parameters, ("zones", zone, "sedimentation_velocity"), 0)]

        if verbose:
            out += f"{values[0][:5]} {' '.join(to_str(value, '{:4d}') for value in values[1:])}\n"

        else:
            out += f"{' '.join(str(x) for x in values)}\n"

    out += ["\n"]

    return out


def _write_convergence_bounds(parameters, verbose, mopr_10=0):
    if mopr_10 != 2:
        return []

    out = ["CONVP\n"]
    out += ["# Read in chemical convergence limits if MOPR(10)=2\n"] if verbose else []

    # Numbers of iterations
    values = [
        _get(parameters, ("options", "n_iteration_1"), 30),
        _get(parameters, ("options", "n_iteration_2"), 50),
        _get(parameters, ("options", "n_iteration_3"), 75),
        _get(parameters, ("options", "n_iteration_4"), 100),
    ]

    if verbose:
        out += ["# MAXCHEM1  MAXCHEM2  MAXCHEM3  MAXCHEM4\n"]
        out += " {}\n".format(" ".join(to_str(value, "{:9d}") for value in values))

    else:
        out += f"{' '.join(str(x) for x in values)}\n"

    # Increase/reduce factors
    values = [
        _get(parameters, ("options", "t_increase_factor_1"), 2.0),
        _get(parameters, ("options", "t_increase_factor_2"), 1.5),
        _get(parameters, ("options", "t_increase_factor_3"), 1.0),
        _get(parameters, ("options", "t_reduce_factor_1"), 0.8),
        _get(parameters, ("options", "t_reduce_factor_2"), 0.6),
        _get(parameters, ("options", "t_reduce_factor_3"), 0.5),
    ]

    if verbose:
        out += ["#  DTINCR1   DTINCR2   DTINCR3   DTDECR1   DTDECR2   DTDECR3\n"]
        out += " {}\n".format(" ".join(to_str(value, "{{:9f}}") for value in values))

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
        logging.warning(f"Key {key_str} is not defined. Setting to {default}.")

        return default
        

comments = {
    "nodes": "Nodes",
    "components": "Primary aqueous species",
    "minerals": "Minerals",
    "aqueous_species": "Individual aqueous species",
    "surface_complexes": "Adsorption species",
    "exchange_species": "Exchange species",
}
