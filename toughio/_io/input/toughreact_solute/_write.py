from ...._common import open_file
from .._common import getval, write_ffrecord

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
    parameters : dict
        Parameters to export.
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


def write_buffer(parameters, mopr_10=0, mopr_11=0, verbose=True, sections=None):
    """Write TOUGHREACT solute input file."""
    from ._common import sections as sections_

    # Section filters
    if sections is None:
        sections = sections_.copy()

    sections = set(sections)

    if sections.intersection(
        [
            "output",
            "elements",
            "components",
            "minerals",
            "aqueous_species",
            "surface_complexes",
            "exchange_species",
        ]
    ):
        numbers = _generate_numbers(parameters)

    # Define input file contents
    out = []

    if "title" in sections:
        out += _write_title(parameters, verbose)

    if "options" in sections:
        out += _write_options(parameters, verbose)

    if "filenames" in sections:
        out += _write_filenames(parameters, verbose)

    if "weights_coefficients" in sections:
        out += _write_weights_coefficients(parameters, verbose)

    if "convergence" in sections:
        out += _write_convergence(parameters, verbose)

    if "output" in sections:
        out += _write_output(parameters, numbers, verbose)

    if "elements" in sections:
        out += _write_elements(parameters, numbers["NWNOD"], verbose)

    if "components" in sections:
        out += _write_indices_names(parameters, "components", numbers["NWCOM"], verbose)

    if "minerals" in sections:
        out += _write_indices_names(parameters, "minerals", numbers["NWMIN"], verbose)

    if "aqueous_species" in sections:
        out += _write_indices_names(
            parameters, "aqueous_species", numbers["NWAQ"], verbose
        )

    if "surface_complexes" in sections:
        out += _write_indices_names(
            parameters, "surface_complexes", numbers["NWADS"], verbose
        )

    if "exchange_species" in sections:
        out += _write_indices_names(
            parameters, "exchange_species", numbers["NWEXC"], verbose
        )

    if "default" in sections:
        out += _write_default(parameters, verbose, mopr_11)

    if "zones" in sections:
        out += _write_zones(parameters, verbose, mopr_11)

    if "convergence_bounds" in sections:
        out += _write_convergence_bounds(parameters, verbose, mopr_10)

    if "end" in sections:
        out += ["end"]

    if "end_comments" in sections and "end_comments" in parameters:
        out += _write_end_comments(parameters)

    return "\n".join(out)


def _generate_numbers(parameters):
    """Generate numbers of outputs."""
    output = parameters["output"]
    nwnod = len(output["elements"]) if "elements" in output else 0
    nwcom = len(output["components"]) if "components" in output else 0
    nwmin = len(output["minerals"]) if "minerals" in output else 0
    nwaq = len(output["aqueous_species"]) if "aqueous_species" in output else 0
    nwads = len(output["surface_complexes"]) if "surface_complexes" in output else 0
    nwexc = len(output["exchange_species"]) if "exchange_species" in output else 0

    numbers = {
        "NWNOD": -nwnod,
        "NWCOM": nwcom,
        "NWMIN": nwmin,
        "NWAQ": nwaq,
        "NWADS": nwads,
        "NWEXC": nwexc,
    }

    if numbers["NWCOM"]:
        if isinstance(parameters["output"]["components"][0], str):
            numbers["NWCOM"] *= -1

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
    """Write title."""
    out = ["# Title"] if verbose else []
    out += [getval(parameters, "title", "")]

    return out


def _write_options(parameters, verbose):
    """Write options."""
    out = []

    # Record 2
    values = [
        to_int(getval(parameters, ("flags", "iteration_scheme"), 0)),
        to_int(getval(parameters, ("flags", "reactive_surface_area"), 0)),
        to_int(getval(parameters, ("flags", "solver"), 0)),
        to_int(getval(parameters, ("flags", "n_subiteration"), 0)),
        to_int(getval(parameters, ("flags", "gas_transport"), 0)),
        to_int(getval(parameters, ("flags", "verbosity"), 0)),
        to_int(getval(parameters, ("flags", "feedback"), 0)),
        to_int(getval(parameters, ("flags", "coupling"), 0)),
        0,
    ]

    out += (
        ["# ISPIA ITERSFA  ISOLVC   NGAMM   NGAS1 ICHDUMP    KCPL ICO2H2O iTDS_REACT"]
        if verbose
        else []
    )
    fmt = ["{:7d}"] * 8 + ["{:10d}"]
    out += write_ffrecord(values, verbose, fmt)

    # Record 3
    values = [
        to_float(getval(parameters, ("options", "sl_min"), 0.0)),
        to_float(getval(parameters, ("options", "rcour"), 0.0)),
        to_float(getval(parameters, ("options", "ionic_strength_max"), 0.0)),
        to_float(getval(parameters, ("options", "mineral_gas_factor"), 0.0)),
    ]

    out += ["#  SL1MIN     RCOUR    STIMAX    CNFACT"] if verbose else []
    out += write_ffrecord(values, verbose, float_fmt="{{:9f}}")

    return out


def _write_filenames(parameters, verbose):
    """Write file names."""
    out = ["# Input and output file names"] if verbose else []
    values = [
        str(getval(parameters, ("files", "thermodynamic_input"), "")),
        str(getval(parameters, ("files", "iteration_output"), "")),
        str(getval(parameters, ("files", "plot_output"), "")),
        str(getval(parameters, ("files", "solid_output"), "")),
        str(getval(parameters, ("files", "gas_output"), "")),
        str(getval(parameters, ("files", "time_output"), "")),
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
    out = ["#   ITIME      WUPC     DFFUN    DFFUNG"] if verbose else []
    values = [
        to_float(getval(parameters, ("options", "w_time"), 0.0)),
        to_float(getval(parameters, ("options", "w_upstream"), 0.0)),
        to_float(getval(parameters, ("options", "aqueous_diffusion_coefficient"), 0.0)),
        to_float(
            getval(parameters, ("options", "molecular_diffusion_coefficient"), 0.0)
        ),
    ]

    out += write_ffrecord(values, verbose, float_fmt="{{:9f}}")

    return out


def _write_convergence(parameters, verbose):
    """Write convergence criterion."""
    out = (
        ["#MAXITPTR     TOLTR  MAXITPCH     TOLCH     TOLMB     TOLDC     TOLDR"]
        if verbose
        else []
    )
    values = [
        to_int(getval(parameters, ("options", "n_iteration_tr"), 0)),
        to_float(getval(parameters, ("options", "eps_tr"), 0.0)),
        to_int(getval(parameters, ("options", "n_iteration_ch"), 0)),
        to_float(getval(parameters, ("options", "eps_ch"), 0.0)),
        to_float(getval(parameters, ("options", "eps_mb"), 0.0)),
        to_float(getval(parameters, ("options", "eps_dc"), 0.0)),
        to_float(getval(parameters, ("options", "eps_dr"), 0.0)),
    ]

    out += write_ffrecord(values, verbose, int_fmt="{:9d}", float_fmt="{{:9f}}")

    return out


def _write_output(parameters, numbers, verbose):
    """Write output control variables."""
    out = (
        ["# NWTI  NWNOD  NWCOM  NWMIN   NWAQ  NWADS  NWEXC   ICON    MIN   IGAS"]
        if verbose
        else []
    )
    values = [
        to_int(getval(parameters, ("options", "n_cycle_print"), 0)),
        to_int(numbers["NWNOD"]),
        to_int(numbers["NWCOM"]),
        to_int(numbers["NWMIN"]),
        to_int(numbers["NWAQ"]),
        to_int(numbers["NWADS"]),
        to_int(numbers["NWEXC"]),
        to_int(getval(parameters, ("flags", "aqueous_concentration_unit"), 0)),
        to_int(getval(parameters, ("flags", "mineral_unit"), 0)),
        to_int(getval(parameters, ("flags", "gas_concentration_unit"), 0)),
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
        out += [f"{x[:20]}" for x in getval(parameters, ("output", key), [])]
        out += [""]

    return out


def _write_default(parameters, verbose, mopr_11=0):
    """Write default chemical property zones."""
    out = (
        ["#IZIWDF IZBWDF IZMIDF IZGSDF IZADDF IZEXDF IZPPDF IZKDDF IZBGDF"]
        if verbose
        else []
    )
    values = [
        to_int(getval(parameters, ("default", "initial_water"), 0)),
        to_int(getval(parameters, ("default", "injection_water"), 0)),
        to_int(getval(parameters, ("default", "mineral"), 0)),
        to_int(getval(parameters, ("default", "initial_gas"), 0)),
        to_int(getval(parameters, ("default", "adsorption"), 0)),
        to_int(getval(parameters, ("default", "cation_exchange"), 0)),
        to_int(getval(parameters, ("default", "permeability_porosity"), 0)),
        to_int(getval(parameters, ("default", "linear_kd"), 0)),
        to_int(getval(parameters, ("default", "injection_gas"), 0)),
    ]

    if mopr_11 != 1:
        if "element" in parameters["default"]:
            values += [parameters["default"]["element"]]

    else:
        values += [getval(parameters, ("default", "sedimentation_velocity"), 0)]

    tmp = write_ffrecord(values, verbose, int_fmt="{:6d}", float_fmt="{{:9f}}")
    out += [f" {tmp[0]}"] if verbose else tmp

    return out


def _write_zones(parameters, verbose, mopr_11=0):
    """Write chemical property zones."""
    out = (
        ["#ELEM NSEQ NADD IZIW IZBW IZMI IZGS IZAD IZEX IZPP IZKD IZBG"]
        if verbose
        else []
    )

    if "zones" not in parameters or not parameters["zones"]:
        out += [""]

        return out

    # Do not use items() for better warning logging in function getval
    for zone in parameters["zones"]:
        values = [
            zone,
            to_int(getval(parameters, ("zones", zone, "nseq"), 0)),
            to_int(getval(parameters, ("zones", zone, "nadd"), 0)),
            to_int(getval(parameters, ("zones", zone, "initial_water"), 0)),
            to_int(getval(parameters, ("zones", zone, "injection_water"), 0)),
            to_int(getval(parameters, ("zones", zone, "mineral"), 0)),
            to_int(getval(parameters, ("zones", zone, "initial_gas"), 0)),
            to_int(getval(parameters, ("zones", zone, "adsorption"), 0)),
            to_int(getval(parameters, ("zones", zone, "cation_exchange"), 0)),
            to_int(getval(parameters, ("zones", zone, "permeability_porosity"), 0)),
            to_int(getval(parameters, ("zones", zone, "linear_kd"), 0)),
            to_int(getval(parameters, ("zones", zone, "injection_gas"), 0)),
        ]

        if mopr_11 != 1:
            if "element" in parameters["zones"][zone]:
                values += [parameters["zones"][zone]["element"]]

        else:
            values += [
                getval(parameters, ("zones", zone, "sedimentation_velocity"), 0.0)
            ]

        out += write_ffrecord(
            values, verbose, int_fmt="{:4d}", float_fmt="{{:9f}}", str_fmt="{:5}"
        )

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
        to_int(getval(parameters, ("options", "n_iteration_1"), 30), 30),
        to_int(getval(parameters, ("options", "n_iteration_2"), 50), 50),
        to_int(getval(parameters, ("options", "n_iteration_3"), 75), 75),
        to_int(getval(parameters, ("options", "n_iteration_4"), 100), 100),
    ]

    out += ["#MAXCHEM1  MAXCHEM2  MAXCHEM3  MAXCHEM4"] if verbose else []
    out += write_ffrecord(values, verbose, int_fmt="{:9d}")

    # Increase/reduce factors
    values = [
        to_float(getval(parameters, ("options", "t_increase_factor_1"), 2.0), 2.0),
        to_float(getval(parameters, ("options", "t_increase_factor_2"), 1.5), 1.5),
        to_float(getval(parameters, ("options", "t_increase_factor_3"), 1.0), 1.0),
        to_float(getval(parameters, ("options", "t_reduce_factor_1"), 0.8), 0.8),
        to_float(getval(parameters, ("options", "t_reduce_factor_2"), 0.6), 0.6),
        to_float(getval(parameters, ("options", "t_reduce_factor_3"), 0.5), 0.5),
    ]

    out += (
        ["# DTINCR1   DTINCR2   DTINCR3   DTDECR1   DTDECR2   DTDECR3"]
        if verbose
        else []
    )
    out += write_ffrecord(values, verbose, float_fmt="{{:9f}}")

    return out


def _write_end_comments(parameters):
    """Write end comments."""
    end_comments = getval(parameters, "end_comments", "")

    return [end_comments] if isinstance(end_comments, str) else end_comments


def to_int(x, default=0):
    """Handle nones in integer conversion."""
    return int(x) if x is not None else default


def to_float(x, default=0.0):
    """Handle nones in floating point conversion."""
    return float(x) if x is not None else default


comments = {
    "nodes": "Nodes",
    "components": "Primary aqueous species",
    "minerals": "Minerals",
    "aqueous_species": "Individual aqueous species",
    "surface_complexes": "Adsorption species",
    "exchange_species": "Exchange species",
}
