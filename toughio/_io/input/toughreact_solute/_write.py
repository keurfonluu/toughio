from .._common import getval, write_ffrecord
from ...._common import open_file

__all__ = [
    "write",
]


def write(filename, parameters, mopr_10=0, mopr_11=0, verbose=True):
    """
    Write TOUGHREACT solute input file.

    Parameters
    ----------
    filename : str
        Input file name.
    mopr_10 : int, optional, default 0
        MOPR(10) value in file 'flow.inp'.
    mopr_11 : int, optional, default 0
        MOPR(11) value in file 'flow.inp'.
    verbose : bool, optional, default True
        If `True`, add comments to describe content of file.

    """
    buffer = write_buffer(parameters, mopr_10, mopr_11, verbose)
    with open_file(filename, "w") as f:
        for record in buffer:
            f.write(record)


def write_buffer(parameters, mopr_10=0, mopr_11=0, verbose=True):
    """Write TOUGHREACT solute input file."""
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
    out += ["end"]

    return "\n".join(out)


def _generate_numbers(parameters):
    """Generate numbers of outputs."""
    numbers = {
        "NWNOD": -len(getval(parameters, ("output", "elements"), [])),
        "NWCOM": len(getval(parameters, ("output", "components"), [])),
        "NWMIN": len(getval(parameters, ("output", "minerals"), [])),
        "NWAQ": len(getval(parameters, ("output", "aqueous_species"), [])),
        "NWADS": len(getval(parameters, ("output", "surface_complexes"), [])),
        "NWEXC": len(getval(parameters, ("output", "exchange_species"), [])),
    }

    if numbers["NWCOM"]:
        if isinstance(parameters["output"]["components"][0], str):
            numbers["NWCOM"] *= -1

    if numbers["NWMIN"]:
        parameters["output"]["minerals"][0]
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
    """Write title."""
    out = ["# Title"] if verbose else []
    out += [getval(parameters, "title", "")]

    return out


def _write_options(parameters, verbose):
    """Write options."""
    out = []

    # Record 2
    values = [
        getval(parameters, ("flags", "iteration_scheme"), 0),
        getval(parameters, ("flags", "reactive_surface_area"), 0),
        getval(parameters, ("flags", "solver"), 0),
        getval(parameters, ("flags", "n_subiteration"), 0),
        getval(parameters, ("flags", "gas_transport"), 0),
        getval(parameters, ("flags", "verbosity"), 0),
        getval(parameters, ("flags", "feedback"), 0),
        getval(parameters, ("flags", "coupling"), 0),
        0,
    ]

    out += ["# ISPIA ITERSFA  ISOLVC   NGAMM   NGAS1 ICHDUMP    KCPL ICO2H2O iTDS_REACT"] if verbose else []
    fmt = ["{:7d}"] * 8 + ["{:10d}"]
    out += write_ffrecord(values, verbose, fmt)

    # Record 3
    values = [
        getval(parameters, ("options", "sl_min"), 0.0),
        getval(parameters, ("options", "rcour"), 0.0),
        getval(parameters, ("options", "ionic_strength_max"), 0.0),
        getval(parameters, ("options", "mineral_gas_factor"), 0.0),
    ]

    out += ["#   SL1MIN     RCOUR    STIMAX    CNFACT"] if verbose else []
    out += write_ffrecord(values, verbose, float_fmt="{{:9f}}")

    return out


def _write_filenames(parameters, verbose):
    """Write file names."""
    out = ["# Input and output file names"] if verbose else []
    values = [
        getval(parameters, ("files", "thermodynamic_input"), ""),
        getval(parameters, ("files", "iteration_output"), ""),
        getval(parameters, ("files", "plot_output"), ""),
        getval(parameters, ("files", "solid_output"), ""),
        getval(parameters, ("files", "gas_output"), ""),
        getval(parameters, ("files", "time_output"), ""),
    ]

    if verbose:
        out += [f"{values[0]:<20}  ! Thermodynamic database"]
        out += [f"{values[1]:<20}  ! Iteration information"]
        out += [f"{values[2]:<20}  ! Aqueous concentrations in Tecplot form"]
        out += [f"{values[3]:<20}  ! Mineral data in Tecplot form"]
        out += [f"{values[4]:<20}  ! Gas data in Tecplot form"]
        out += [f"{values[5]:<20}  ! Concentrations at specific elements over time"]

    else:
        out += [f"{value}" for value in values]

    return out


def _write_weights_coefficients(parameters, verbose):
    """Write weights and diffusion coefficients."""
    out = ["#    ITIME      WUPC     DFFUN    DFFUNG"] if verbose else []
    values = [
        getval(parameters, ("options", "w_time"), 0.0),
        getval(parameters, ("options", "w_upstream"), 0.0),
        getval(parameters, ("options", "aqueous_diffusion_coefficient"), 0.0),
        getval(parameters, ("options", "molecular_diffusion_coefficient"), 0.0),
    ]

    out += write_ffrecord(values, verbose, float_fmt="{{:9f}}")

    return out


def _write_convergence(parameters, verbose):
    """Write convergence criterion."""
    out = ["# MAXITPTR     TOLTR  MAXITPCH     TOLCH     TOLMB     TOLDC     TOLDR"] if verbose else []
    values = [
        getval(parameters, ("options", "n_iteration_tr"), 0),
        getval(parameters, ("options", "eps_tr"), 0.0),
        getval(parameters, ("options", "n_iteration_ch"), 0),
        getval(parameters, ("options", "eps_ch"), 0.0),
        getval(parameters, ("options", "eps_mb"), 0.0),
        getval(parameters, ("options", "eps_dc"), 0.0),
        getval(parameters, ("options", "eps_dr"), 0.0),
    ]

    out += write_ffrecord(values, verbose, int_fmt="{:9d}", float_fmt="{{:9f}}")

    return out


def _write_output(parameters, numbers, verbose):
    """Write output control variables."""
    out = ["#  NWTI  NWNOD  NWCOM  NWMIN   NWAQ  NWADS  NWEXC   ICON    MIN   IGAS"] if verbose else []
    values = [
        getval(parameters, ("options", "n_cycle_print"), 0),
        numbers["NWNOD"],
        numbers["NWCOM"],
        numbers["NWMIN"],
        numbers["NWAQ"],
        numbers["NWADS"],
        numbers["NWEXC"],
        getval(parameters, ("flags", "aqueous_concentration_unit"), 0),
        getval(parameters, ("flags", "mineral_unit"), 0),
        getval(parameters, ("flags", "gas_concentration_unit"), 0),
    ]

    out += write_ffrecord(values, verbose, int_fmt="{:6d}")

    return out


def _write_elements(parameters, n, verbose):
    """Write list of grid blocks."""
    out = [f"# {comments['nodes']}"] if verbose else []

    if n == 0:
        out += [""]

        return out
    
    out += [f"{x[:5]}" for x in getval(parameters, ("output", "elements"), [])]
    out += [""]

    return out


def _write_indices_names(parameters, key, n, verbose):
    """Write indices or names."""
    out = [f"# {comments[key]}"] if verbose else []

    if n == 0:
        out += [""]

        return out

    if n > 0:
        out += [f"{' '.join(str(x) for x in getval(parameters, ('output', key), []))}"]

    else:
        out += [f"{x[:20]}" for x in getval(parameters, ('output', key), [])]
        out += [""]

    return out


def _write_default(parameters, verbose, mopr_11=0):
    """Write default chemical property zones."""
    out = [f"#IZIWDF IZBWDF IZMIDF IZGSDF IZADDF IZEXDF IZPPDF IZKDDF IZBGDF"] if verbose else []
    values = [
        getval(parameters, ("default", "initial_water"), 0),
        getval(parameters, ("default", "injection_water"), 0),
        getval(parameters, ("default", "mineral"), 0),
        getval(parameters, ("default", "initial_gas"), 0),
        getval(parameters, ("default", "adsorption"), 0),
        getval(parameters, ("default", "cation_exchange"), 0),
        getval(parameters, ("default", "permeability_porosity"), 0),
        getval(parameters, ("default", "linear_kd"), 0),
        getval(parameters, ("default", "injection_gas"), 0),
    ]

    if mopr_11 != 1:
        if "element" in parameters["default"]:
            values += [parameters["default"]["element"]]

    else:
        values += [getval(parameters, ("default", "sedimentation_velocity"), 0)]

    out += write_ffrecord(values, verbose, int_fmt="{:6d}", float_fmt="{{:9f}}")

    return out


def _write_zones(parameters, verbose, mopr_11=0):
    """Write chemical property zones."""
    out = ["#ELEM NSEQ NADD IZIW IZBW IZMI IZGS IZAD IZEX IZPP IZKD IZBG"] if verbose else []
    
    if "zones" not in parameters or not parameters["zones"]:
        out += [""]

        return out
    
    # Do not use items() for better warning logging in function getval
    for zone in parameters["zones"]:
        values = [
            zone,
            getval(parameters, ("zones", zone, "nseq"), 0),
            getval(parameters, ("zones", zone, "nadd"), 0),
            getval(parameters, ("zones", zone, "initial_water"), 0),
            getval(parameters, ("zones", zone, "injection_water"), 0),
            getval(parameters, ("zones", zone, "mineral"), 0),
            getval(parameters, ("zones", zone, "initial_gas"), 0),
            getval(parameters, ("zones", zone, "adsorption"), 0),
            getval(parameters, ("zones", zone, "cation_exchange"), 0),
            getval(parameters, ("zones", zone, "permeability_porosity"), 0),
            getval(parameters, ("zones", zone, "linear_kd"), 0),
            getval(parameters, ("zones", zone, "injection_gas"), 0),
        ]

        if mopr_11 != 1:
            if "element" in parameters["zones"][zone]:
                values += [parameters["zones"][zone]["element"]]

        else:
            values += [getval(parameters, ("zones", zone, "sedimentation_velocity"), 0.0)]

        out += write_ffrecord(values, verbose, int_fmt="{:4d}", float_fmt="{{:9f}}")

    out += [""]

    return out


def _write_convergence_bounds(parameters, verbose, mopr_10=0):
    """Write convergence bounds."""
    if mopr_10 != 2:
        return []

    out = ["CONVP"]
    out += ["# Read in chemical convergence limits if MOPR(10)=2"] if verbose else []

    # Numbers of iterations
    values = [
        getval(parameters, ("options", "n_iteration_1"), 30),
        getval(parameters, ("options", "n_iteration_2"), 50),
        getval(parameters, ("options", "n_iteration_3"), 75),
        getval(parameters, ("options", "n_iteration_4"), 100),
    ]

    out += ["# MAXCHEM1  MAXCHEM2  MAXCHEM3  MAXCHEM4"] if verbose else []
    out += write_ffrecord(values, verbose, int_fmt="{:9d}")

    # Increase/reduce factors
    values = [
        getval(parameters, ("options", "t_increase_factor_1"), 2.0),
        getval(parameters, ("options", "t_increase_factor_2"), 1.5),
        getval(parameters, ("options", "t_increase_factor_3"), 1.0),
        getval(parameters, ("options", "t_reduce_factor_1"), 0.8),
        getval(parameters, ("options", "t_reduce_factor_2"), 0.6),
        getval(parameters, ("options", "t_reduce_factor_3"), 0.5),
    ]

    out += ["#  DTINCR1   DTINCR2   DTINCR3   DTDECR1   DTDECR2   DTDECR3"] if verbose else []
    out += write_ffrecord(values, verbose, float_fmt="{{:9f}}")

    return out
        

comments = {
    "nodes": "Nodes",
    "components": "Primary aqueous species",
    "minerals": "Minerals",
    "aqueous_species": "Individual aqueous species",
    "surface_complexes": "Adsorption species",
    "exchange_species": "Exchange species",
}
