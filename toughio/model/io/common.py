# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

import numpy as np
from functools import wraps

__all__ = [
    "Parameters",
    "default",
    "eos",
    "header",
    "new",
    "block",
]


_mop = { k+1: v for k, v in enumerate([
    None, 0, 0, 0, None, 0, 2, None,
    0, 0, 0, 0, 0, None, None, 4,
    None, None, None, None, 3, None, None, None, 
]) }

_options = {
    "n_iteration": None,
    "n_cycle": None,
    "n_second": None,
    "n_cycle_print": None,
    "verbosity": None,
    "MOP": dict(_mop),
    "temperature_dependance_gas": None,
    "effective_strength_vapor": None,
    "t_ini": None,
    "t_max": None,
    "t_step": None,
    "t_step_max": None,
    "t_reduce_factor": None,
    "gravity": 9.81,
    "mesh_scale_factor": None,
    "eps1": None,
    "eps2": None,
    "w_upstream": None,
    "w_newton": None,
    "derivative_factor": None,
    "incon": [ None ] * 4,
}

_Parameters = {
    "title": "",
    "eos": "",
    "flac": False,
    "isothermal": False,
    "nover": False,
    "rocks": {},
    "options": dict(_options),
    "solver": None,
    "times": None,
    "foft": None,
    "coft": None,
    "goft": None,
    "default": {},
}

Parameters = dict(_Parameters)

default = {
    "density": None,
    "porosity": None,
    "permeability": None,
    "conductivity": None,
    "specific_heat": None,
    "compressibility": None,
    "expansivity": None,
    "conductivity_dry": None,
    "tortuosity": None,
    "b_coeff": None,
    "xkd3": None,
    "xkd4": None,
    "relative_permeability": {
        "id": None,
        "parameters": [],
    },
    "capillary_pressure": {
        "id": None,
        "parameters": [],
    },
    "permeability_law": {
        "id": 1,
        "parameters": [],
    },
    "equivalent_pore_pressure": {
        "id": 3,
        "parameters": [ 0.2684e8, -0.1991e8, 0.3845 ],
    },
}

eos = {
    "eos1": [],
    "eos2": [],
    "eos3": [],
    "eos4": [],
    "eos5": [],
    "eos7": [],
    "eos8": [],
    "eos9": [],
    "eosmvoc": [],
    "eoswasg": [],
    "eco2n": [ 3, 4, 3, 6 ],
    "eco2n_v2": [ 3, 4, 3, 6 ],
    "eco2m": [ 3, 4, 3, 6 ],
}

header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"


def new():
    """
    Reset parameter values to default.
    """
    Parameters.update(_Parameters)
    Parameters["rocks"] = {}
    Parameters["options"].update(_options)
    Parameters["options"]["MOP"].update(_mop)


def block(keyword, multi = False):
    """
    Decorator for block writing functions.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            out = [ "{:5}{}\n".format(keyword, header) ]
            out += func(*args, **kwargs)
            out += [ "\n" ] if multi else []
            return out
        return wrapper
    return decorator