# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

import numpy as np

from .common import (
    block,
    default,
)

__all__ = [
    "write",
]


def write(filename = "INFILE"):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str, optional, default 'INFILE'
        Output file name.
    """
    assert isinstance(filename, str)

    # Import current parameter settings
    from .common import Parameters, eos

    # Check that EOS is defined (for block MULTI)
    if Parameters["eos"] not in eos.keys():
        raise ValueError(
            "EOS '{}' is unknown or not supported.".format(Parameters["eos"])
        )

    # Define input file contents
    out = [ "* {:78}\n".format(Parameters["title"]) ]
    out += _write_rocks(Parameters)
    if Parameters["flac"]:
        out += _write_flac(Parameters)
    out += _write_multi(Parameters)
    if Parameters["eos"] in { "eco2n", "eco2n_v2", "eco2m" }:
        out += _write_selec(Parameters)
    out += _write_start()
    out += _write_param(Parameters)
    if Parameters["times"]:
        out += _write_times(Parameters)
    out += _write_gener(Parameters)
    if Parameters["nover"]:
        out += _write_nover()
    out += _write_endcy()
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
            for i in range(int(np.ceil(n/ncol))) ]
    return [ _write_record(r)[0] for r in rec ]


def _add_record(data, id_fmt = "{:>5g}     "):
    """
    Return a list with a single string for additional records.
    """
    n = len(data["parameters"])
    rec = [ ( data["id"], id_fmt ) ]
    rec += [ ( v, "{:>10.3e}" ) for v in data["parameters"][:min(n, 7)] ]
    return _write_record(_format_data(rec))


@block("ROCKS", multi = True)
def _write_rocks(Parameters):
    """
    Block ROCKS.
    """
    out = []
    for k, v in Parameters["rocks"].items():
        # Load data
        tmp = default.copy()
        tmp.update(Parameters["default"])
        tmp.update(v)

        # Number of additional lines to write per rock
        nad = 0
        nad += 1 if tmp["relative_permeability"]["id"] is not None else 0
        nad += 1 if tmp["capillary_pressure"]["id"] is not None else 0

        # Permeability
        per = tmp["permeability"]
        per = [ per ] * 3 if isinstance(per, float) else per
        assert isinstance(per, (list, tuple, np.ndarray)) and len(per) == 3

        # Record 1
        out += _write_record(_format_data([
            ( k, "{:5.5}" ),
            ( nad if nad else None, "{:>5g}" ),
            ( tmp["density"], "{:>10.4e}" ) ,
            ( tmp["porosity"], "{:>10.4e}" ),
            ( per[0], "{:>10.4e}" ),
            ( per[1], "{:>10.4e}" ),
            ( per[2], "{:>10.4e}" ),
            ( tmp["conductivity"], "{:>10.4e}" ),
            ( tmp["specific_heat"], "{:>10.4e}" ),
        ]))

        # Record 2
        out += _write_record(_format_data([
            ( tmp["compressibility"], "{:>10.4e}" ),
            ( tmp["expansivity"], "{:>10.4e}" ),
            ( tmp["conductivity_dry"], "{:>10.4e}" ),
            ( tmp["tortuosity"], "{:>10.4e}" ),
            ( tmp["b_coeff"], "{:>10.4e}" ),
            ( tmp["xkd3"], "{:>10.4e}" ),
            ( tmp["xkd4"], "{:>10.4e}" ),
        ]))

        # Relative permeability
        out += _add_record(tmp["relative_permeability"]) if nad >= 1 else []

        # Capillary pressure
        out += _add_record(tmp["capillary_pressure"]) if nad >= 2 else []
    return out


@block("FLAC", multi = True)
def _write_flac(Parameters):
    """
    Block FLAC.
    """
    out = [ "\n" ]
    for v in Parameters["rocks"].values():
        # Load data
        tmp = default.copy()
        tmp.update(Parameters["default"])
        tmp.update(v)

        # Permeability law
        out += _add_record(tmp["permeability_law"], "{:>10g}")

        # Equivalent pore pressure
        out += _add_record(tmp["equivalent_pore_pressure"])
    return out


@block("MULTI", multi = False)
def _write_multi(Parameters):
    """
    Block MULTI.
    """
    from .common import eos
    out = eos[Parameters["eos"]].copy()
    out[1] -= 1 if Parameters["isothermal"] else 0
    return [ ("{:>5d}"*4 + "\n").format(*out) ]


@block("SELEC", multi = False)
def _write_selec(Parameters):
    """
    Block SELEC.
    """
    out = []

    # Load data
    data = Parameters["selections"]

    # Record 1
    out += _write_record(_format_data([
        ( v, "{:>5}" ) for v in data.values()
    ]))

    # Record 2
    data = Parameters["extra_selections"]
    if data:
        n = len(data)
        out += _write_multi_record(_format_data([
            ( i, "{:>10.3e}" ) for i in data
        ]))
    return out


@block("START", multi = False)
def _write_start():
    """
    Block START.
    """
    from .common import header
    out = "{:5}{}\n".format("----*", header)
    return [ out[:11] + "MOP: 123456789*123456789*1234" + out[40:] ]


@block("PARAM", multi = False)
def _write_param(Parameters):
    """
    Block PARAM.
    """
    out = []

    # Load data
    from .common import options
    data = default.copy()
    data.update(Parameters["options"])

    # Record 1
    _mop = Parameters["extra_options"]
    mop = _format_data([ ( _mop[k], "{:>1g}" )
                            for k in sorted(_mop.keys()) ])
    out += _write_record(_format_data([
        ( data["n_iteration"], "{:>2g}" ),
        ( data["verbosity"], "{:>2g}" ),
        ( data["n_cycle"], "{:>4g}" ),
        ( data["n_second"], "{:>4g}" ),
        ( data["n_cycle_print"], "{:>4g}" ),
        ( "{}".format("".join(mop)), "{:>24}" ),
        ( None, "{:>10}" ),
        ( data["temperature_dependance_gas"], "{:>10.4e}" ),
        ( data["effective_strength_vapor"], "{:>10.4e}" ),
    ]))

    # Record 2
    out += _write_record(_format_data([
        ( data["t_ini"], "{:>10.4e}" ),
        ( data["t_max"], "{:>10.4e}" ),
        ( data["t_step"], "{:>10.4e}" ),
        ( data["t_step_max"], "{:>10.4e}" ),
        ( None, "{:>10g}" ),
        ( data["gravity"], "{:>10.4e}" ),
        ( data["t_reduce_factor"], "{:>10.4e}" ),
        ( data["mesh_scale_factor"], "{:>10.4e}" ),
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


@block("TIMES", multi = False)
def  _write_times(Parameters):
    """
    Block TIMES.
    """
    data = Parameters["times"]
    n = len(data)
    out = _write_record(_format_data([
        ( n, "{:>5g}" ),
    ]))
    out += _write_multi_record(_format_data([
        ( i, "{:>10.4e}" ) for i in data
    ]))
    return out


@block("GENER", multi = True)
def _write_gener(Parameters):
    """
    Block GENER.
    """
    from .common import generators

    out = []
    for k, v in Parameters["generators"].items():    
        # Load data
        data = generators.copy()
        data.update(v)

        # Record 1
        out += _write_record(_format_data([
            ( k, "{:5.5}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( None, "{:>5g}" ),
            ( data["type"], "{:4g} " ),
            ( data["rate"], "{:>10.3e}" ),
            ( data["specific_enthalpy"], "{:>10.3e}" ),
            ( data["layer_thickness"], "{:>10.3e}" ),
        ]))
    return out


@block("NOVER", multi = False)
def _write_nover():
    """
    Block NOVER.
    """
    return []


@block("ENDCY", multi = False)
def _write_endcy():
    """
    Block ENDCY.
    """
    return []