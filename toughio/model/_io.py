from __future__ import division

import numpy

import json

from ._common import (
    default,
    set_parameters
)

__all__ = [
    "read_json",
    "to_file",
    "to_json",
]


def read_json(filename, return_parameters = False):
    """
    Import TOUGH input file.
    
    Parameters
    ----------
    filename : str
        Input file name.
    return_parameters : bool, optional, default False
        If `True`, return parameters as a dict. Otherwise, overwrite
        current `toughio.model.Parameters`.
    
    Returns
    -------
    dict
        TOUGH input parameters. Only if ``return_parameters == True``.
    """
    def to_int(data):
        """
        Return dict with integer keys instead of strings.
        """
        return { int(k): data[k] for k in sorted(data.keys()) }
    
    assert isinstance(filename, str)
    with open(filename, "r") as f:
        parameters = json.load(f)

    if "extra_options" in parameters.keys():
        parameters["extra_options"] = to_int(parameters["extra_options"])
    if "selections" in parameters.keys():
        parameters["selections"] = to_int(parameters["selections"])

    if return_parameters:
        return parameters
    else:
        set_parameters(parameters)


def to_file(filename = "INFILE", parameters = None):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str, optional, default 'INFILE'
        Output file name.
    parameters : dict or None, optional, default None
        Parameters to export.
    """
    assert isinstance(filename, str)
    assert parameters is None or isinstance(parameters, dict)

    if parameters is None:
        from ._common import Parameters as parameters

    with open(filename, "w") as f:
        for record in write_buffer(parameters):
            f.write(record)


def to_json(filename = "INFILE.json", parameters = None):
    """
    Export TOUGH input file to json format.

    Parameters
    ----------
    filename : str, optional, default 'INFILE.json'
        Output file name.
    parameters : dict or None, optional, default None
        Parameters to export.
    """
    assert isinstance(filename, str)
    assert parameters is None or isinstance(parameters, dict)

    if parameters is None:
        from ._common import Parameters as parameters

    with open(filename, "w") as f:
        json.dump(parameters, f, indent = 4)


def write_buffer(parameters):
    """
    Write TOUGH input file as a list of 80-character long record strings.
    """
    from ._common import eos, eos_select

    # Check that EOS is defined (for block MULTI)
    if parameters["isothermal"] and parameters["eos"] not in eos.keys():
        raise ValueError(
            "EOS '{}' is unknown or not supported.".format(parameters["eos"])
        )

    # Define input file contents
    out = [ "{:80}\n".format(parameters["title"]) ]
    out += _write_rocks(parameters)
    out += _write_flac(parameters) if parameters["flac"] else []
    out += _write_multi(parameters) if parameters["eos"] else []
    out += _write_selec(parameters) if parameters["eos"] in eos_select else []
    out += _write_solvr(parameters) if parameters["solver"] else []
    out += _write_start() if parameters["start"] else []
    out += _write_param(parameters)
    out += _write_times(parameters) if parameters["times"] is not None else []
    out += _write_foft(parameters) if parameters["element_history"] is not None else []
    out += _write_coft(parameters) if parameters["connection_history"] is not None else []
    out += _write_goft(parameters) if parameters["generator_history"] is not None else []
    out += _write_gener(parameters) if parameters["generators"] else []
    out += _write_nover() if parameters["nover"] else []
    out += _write_endfi() if parameters["endfi"] else _write_endcy()
    return out


def _format_data(data):
    """
    Return a list of strings given input data and formats.
    """
    def to_str(x, fmt):
        x = "" if x is None or x == "" else x
        if isinstance(x, str):
            return fmt.replace("g", "").replace("e", "").format(x)
        else:
            return fmt.format(x)
    return [ to_str(x, fmt) for x, fmt in data ]


def _write_record(data):
    """
    Return a list with a single string.
    """
    return [ "{:80}\n".format("".join(data)) ]


def _write_multi_record(data, ncol = 8):
    """
    Return a list with multiple strings.
    """
    n = len(data)
    rec = [ data[ncol*i:min(ncol*i+ncol, n)]
            for i in range(int(numpy.ceil(n/ncol))) ]
    return [ _write_record(r)[0] for r in rec ]


def _add_record(data, id_fmt = "{:>5g}     "):
    """
    Return a list with a single string for additional records.
    """
    n = len(data["parameters"])
    rec = [ ( data["id"], id_fmt ) ]
    rec += [ ( v, "{:>10.3e}" ) for v in data["parameters"][:min(n, 7)] ]
    return _write_record(_format_data(rec))


def block(keyword, multi = False, noend = False):
    """
    Decorator for block writing functions.
    """

    def decorator(func):
        from functools import wraps

        from ._common import header

        @wraps(func)
        def wrapper(*args, **kwargs):
            head_fmt = "{:5}{}" if noend else "{:5}{}\n"
            out = [ head_fmt.format(keyword, header) ]
            out += func(*args, **kwargs)
            out += [ "\n" ] if multi else []

            return out

        return wrapper
        
    return decorator


@block("ROCKS", multi = True)
def _write_rocks(parameters):
    """
    TOUGH input ROCKS block data.
    
    Introduces material parameters for up to 27 different reservoir
    domains.
    """
    # Reorder rocks
    if parameters["rocks_order"] is not None:
        order = parameters["rocks_order"]
    else:
        order = parameters["rocks"].keys()

    out = []
    for k in order:
        # Load data
        data = default.copy()
        data.update(parameters["default"])
        data.update(parameters["rocks"][k])

        # Number of additional lines to write per rock
        nad = 0
        nad += 1 if data["relative_permeability"]["id"] is not None else 0
        nad += 1 if data["capillarity"]["id"] is not None else 0

        # Permeability
        per = data["permeability"]
        per = [ per ] * 3 if isinstance(per, float) else per
        assert isinstance(per, (list, tuple, numpy.ndarray)) and len(per) == 3

        # Record 1
        out += _write_record(_format_data([
            ( k, "{:5.5}" ),
            ( nad if nad else None, "{:>5g}" ),
            ( data["density"], "{:>10.4e}" ) ,
            ( data["porosity"], "{:>10.4e}" ),
            ( per[0], "{:>10.4e}" ),
            ( per[1], "{:>10.4e}" ),
            ( per[2], "{:>10.4e}" ),
            ( data["conductivity"], "{:>10.4e}" ),
            ( data["specific_heat"], "{:>10.4e}" ),
        ]))

        # Record 2
        out += _write_record(_format_data([
            ( data["compressibility"], "{:>10.4e}" ),
            ( data["expansion"], "{:>10.4e}" ),
            ( data["conductivity_dry"], "{:>10.4e}" ),
            ( data["tortuosity"], "{:>10.4e}" ),
            ( data["b_coeff"], "{:>10.4e}" ),
            ( data["xkd3"], "{:>10.4e}" ),
            ( data["xkd4"], "{:>10.4e}" ),
        ]))

        # Relative permeability
        out += _add_record(data["relative_permeability"]) if nad >= 1 else []

        # Capillary pressure
        out += _add_record(data["capillarity"]) if nad >= 2 else []
    return out


@block("FLAC", multi = True)
def _write_flac(parameters):
    """
    TOUGH input FLAC block data (optional).

    Introduces mechanical parameters for each material in ROCKS block data.
    """
    # Reorder rocks
    if parameters["rocks_order"]:
        order = parameters["rocks_order"]
    else:
        order = parameters["rocks"].keys()
    
    # Record 1
    out = _write_record(_format_data([
        ( 1 if parameters["creep"] else 0, "{:5g}" ),
        ( parameters["porosity_model"], "{:5g}" ),
    ]))

    # Additional records
    for k in order:
        # Load data
        data = default.copy()
        data.update(parameters["default"])
        data.update(parameters["rocks"][k])

        # Permeability law
        out += _add_record(data["permeability_model"], "{:>10g}")

        # Equivalent pore pressure
        out += _add_record(data["equivalent_pore_pressure"])
    return out


@block("MULTI")
def _write_multi(parameters):
    """
    TOUGH input MULTI block (optional).

    Permits the user to select the number and nature of balance equations
    that will be solved. The keyword MULTI is followed by a single data
    record. For most EOS modules, this data block is not needed, as
    default values are provided internally. Available parameter choices
    are different for different EOS modules.
    """
    from ._common import eos
    out = list(eos[parameters["eos"]])
    out[0] = parameters["n_component"] if parameters["n_component"] else out[0]
    out[1] = out[0] if parameters["isothermal"] else out[0]+1
    out[2] = parameters["n_phase"] if parameters["n_phase"] else out[2]
    return [ ("{:>5d}"*len(out) + "\n").format(*out) ]


@block("SELEC")
def _write_selec(parameters):
    """
    TOUGH input SELEC block (optional).

    Introduces a number of integer and floating point parameters that are
    used for different purposes in different TOUGH modules (EOS7, EOS7R,
    EWASG, T2DM, ECO2N).
    """
    # Load data
    from ._common import select
    data = select.copy()
    data.update(parameters["selections"])

    # Record 1
    out = _write_record(_format_data([
        ( v, "{:>5}" ) for v in data.values()
    ]))

    # Record 2
    if parameters["extra_selections"] is not None:
        out += _write_multi_record(_format_data([
            ( i, "{:>10.3e}" ) for i in parameters["extra_selections"]
        ]))
    return out


@block("SOLVR")
def _write_solvr(parameters):
    """
    TOUGH input SOLVR block (optional).

    Introduces computation parameters, time stepping information, and
    default initial conditions.
    """
    from ._common import solver
    data = solver.copy()
    data.update(parameters["solver"])
    return _write_record(_format_data([
        ( data["method"], "{:1g}  " ),
        ( data["z_precond"], "{:>2g}   " ),
        ( data["o_precond"], "{:>2g}" ),
        ( data["rel_iter_max"], "{:>10.4e}" ),
        ( data["eps"], "{:>10.4e}" ),
    ]))


@block("START")
def _write_start():
    """
    TOUGH input START block (optional).

    A record with START typed in columns 1-5 allows a more flexible
    initialization. More specifically, when START is present, INCON data
    can be in arbitrary order, and need not be present for all grid blocks 
    (in which case defaults will be used). Without START, there must be a
    one-to-one correspondence between the data in blocks ELEME and INCON.
    """
    from ._common import header
    out = "{:5}{}\n".format("----*", header)
    return [ out[:11] + "MOP: 123456789*123456789*1234" + out[40:] ]


@block("PARAM")
def _write_param(parameters):
    """
    TOUGH input PARAM block data.
    
    Introduces computation parameters, time stepping information, and
    default initial conditions.
    """
    # Load data
    from ._common import options
    data = options.copy()
    data.update(parameters["options"])

    # Table
    if not isinstance(data["t_steps"], (list, tuple, numpy.ndarray)):
        data["t_steps"] = [ data["t_steps"] ]

    # Record 1
    from ._common import extra_options
    _mop = extra_options.copy()
    _mop.update(parameters["extra_options"])
    mop = _format_data([ ( _mop[k], "{:>1g}" )
                            for k in sorted(_mop.keys()) ])
    out = _write_record(_format_data([
        ( data["n_iteration"], "{:>2g}" ),
        ( data["verbosity"], "{:>2g}" ),
        ( data["n_cycle"], "{:>4g}" ),
        ( data["n_second"], "{:>4g}" ),
        ( data["n_cycle_print"], "{:>4g}" ),
        ( "{}".format("".join(mop)), "{:>24}" ),
        ( None, "{:>10}" ),
        ( data["temperature_dependence_gas"], "{:>10.4e}" ),
        ( data["effective_strength_vapor"], "{:>10.4e}" ),
    ]))

    # Record 2
    out += _write_record(_format_data([
        ( data["t_ini"], "{:>10.4e}" ),
        ( data["t_max"], "{:>10.4e}" ),
        ( -len(data["t_steps"]), "{:>9g}." ),
        ( data["t_step_max"], "{:>10.4e}" ),
        ( None, "{:>10g}" ),
        ( data["gravity"], "{:>10.4e}" ),
        ( data["t_reduce_factor"], "{:>10.4e}" ),
        ( data["mesh_scale_factor"], "{:>10.4e}" ),
    ]))

    # Record 2.1
    out += _write_multi_record(_format_data([
        ( i, "{:>10.4e}" ) for i in data["t_steps"]
    ]))

    # Record 3
    out += _write_record(_format_data([
        ( data["eps1"], "{:>10.4e}" ),
        ( data["eps2"], "{:>10.4e}" ),
        ( None, "{:>10.4e}" ),
        ( data["w_upstream"], "{:>10.4e}" ),
        ( data["w_newton"], "{:>10.4e}" ),
        ( data["derivative_factor"], "{:>10.4e}" ),
    ]))

    # Record 4
    n = len(data["incon"])
    out += _write_record(_format_data([
        ( i, "{:>20.4e}" ) for i in data["incon"][:min(n, 4)]
    ]))
    return out


@block("TIMES", multi = True)
def  _write_times(parameters):
    """
    TOUGH input TIMES block data (optional).
    
    Permits the user to obtain printout at specified times.
    """
    data = parameters["times"]
    n = len(data)
    out = _write_record(_format_data([
        ( n, "{:>5g}" ),
    ]))
    out += _write_multi_record(_format_data([
        ( i, "{:>10.4e}" ) for i in data
    ]))
    return out


@block("FOFT", multi = True)
def _write_foft(parameters):
    """
    TOUGH input FOFT block data (optional).
    
    Introduces a list of elements (grid blocks) for which time-dependent
    data are to be written out for plotting to a file called FOFT during
    the simulation.
    """
    return _write_record(_format_data([
        ( i, "{:>5g}" ) for i in parameters["element_history"]
    ]))


@block("COFT", multi = True)
def _write_coft(parameters):
    """
    TOUGH input COFT block data (optional).
    
    Introduces a list of connections for which time-dependent data are to
    be written out for plotting to a file called COFT during the
    simulation.
    """
    return _write_record(_format_data([
        ( i, "{:>10g}" ) for i in parameters["connection_history"]
    ]))


@block("GOFT", multi = True)
def _write_goft(parameters):
    """
    TOUGH input GOFT block data (optional).
    
    Introduces a list of sinks/sources for which time-dependent data are
    to be written out for plotting to a file called GOFT during the
    simulation.
    """
    return _write_record(_format_data([
        ( i, "{:>5g}" ) for i in parameters["generator_history"]
    ]))


@block("GENER", multi = True)
def _write_gener(parameters):
    """
    TOUGH input GENER block data (optional).
    
    Introduces sinks and/or sources.
    """
    from ._common import generators

    out = []
    for k, v in parameters["generators"].items():    
        # Load data
        data = generators.copy()
        data.update(v)
        
        # Table
        ltab, itab = None, None
        if data["times"] is not None and isinstance(data["times"], (list, tuple, numpy.ndarray)):
            ltab, itab = len(data["times"]), 1
            assert isinstance(data["rates"], (list, tuple, numpy.ndarray))
            assert ltab > 1 and ltab == len(data["rates"])

        # Record 1
        out += _write_record(_format_data([
            ( k, "{:5.5}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( ltab, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( data["type"], "{:4g}" ),
            ( itab, "{:>1g}" ),
            ( None if ltab else data["rates"], "{:>10.3e}" ),
            ( None if ltab else data["specific_enthalpy"], "{:>10.3e}" ),
            ( data["layer_thickness"], "{:>10.3e}" ),
        ]))

        # Record 2
        if ltab:
            out += _write_multi_record(_format_data([
                ( i, "{:>14.7e}" ) for i in data["times"]
            ]), ncol = 4)

        # Record 3
        if ltab:
            out += _write_multi_record(_format_data([
                ( i, "{:>14.7e}" ) for i in data["rates"]
            ]), ncol = 4)

        # Record 4
        if ltab and data["specific_enthalpy"] is not None:
            if isinstance(data["specific_enthalpy"], (list, tuple, numpy.ndarray)):
                specific_enthalpy = data["specific_enthalpy"]
            else:
                specific_enthalpy = numpy.full(ltab, data["specific_enthalpy"])
            out += _write_multi_record(_format_data([
                ( i, "{:>14.7e}" ) for i in specific_enthalpy
            ]), ncol = 4)
    return out


@block("NOVER")
def _write_nover():
    """
    TOUGH input NOVER block data (optional).
    """
    return []


@block("ENDFI", noend = True)
def _write_endfi():
    """
    TOUGH input ENDFI block data (optional).
    """
    return []


@block("ENDCY", noend = True)
def _write_endcy():
    """
    TOUGH input ENDCY block data (optional).
    """
    return []