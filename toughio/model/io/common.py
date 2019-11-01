# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

import numpy as np
from functools import wraps

__all__ = [
    "Parameters",
    "select",
    "options",
    "extra_options",
    "solver",
    "generators",
    "default",
    "eos",
    "eos_select",
    "header",
    "new",
    "set_parameters",
    "block",
]


_Parameters = {
    "title": "",
    "eos": "",
    "n_component": None,
    "n_phase": None,
    "flac": False,
    "creep": False,
    "porosity_model": 0,
    "isothermal": False,
    "start": True,
    "nover": False,
    "endfi": False,
    "rocks": {},
    "rocks_order": [],
    "options": {},
    "extra_options": {},
    "selections": {},
    "extra_selections": [],
    "solver": {},
    "generators": {},
    "times": [],
    "element_history": [],
    "connection_history": [],
    "generator_history": [],
    "default": {},
}

Parameters = dict(_Parameters)

select = { k+1: None for k in range(16) }

options = {
    "n_iteration": None,
    "n_cycle": None,
    "n_second": None,
    "n_cycle_print": None,
    "verbosity": None,
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
    "incon": [ None for _ in range(4) ],
}

extra_options = { k+1: v for k, v in enumerate([
    None, 0, 0, 0, None, 0, 2, None,
    0, 0, 0, 0, 0, None, None, 4,
    None, None, None, None, 3, None, None, None, 
]) }

solver = {
    "method": 3,
    "z_precond": "Z0",
    "o_precond": "O0",
    "rel_iter_max": 0.1,
    "eps": 1.e-6,
}

generators = {
    "type": None,
    "times": None,
    "rates": None,
    "specific_enthalpy": None,
    "layer_thickness": None,
}

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
    "eos1": [ 1, 2, 2, 6 ],
    "eos2": [ 2, 3, 2, 6 ],
    "eos3": [ 2, 3, 2, 6 ],
    "eos4": [ 2, 3, 2, 6 ],
    "eos5": [ 2, 3, 2, 6 ],
    "eos7": [ 3, 3, 2, 6 ],
    "eos8": [ 3, 3, 3, 6 ],
    "eos9": [ 1, 1, 1, 6 ],
    "eoswasg": [ 3, 4, 3, 6 ],
    "eco2n": [ 3, 4, 3, 6 ],
    "eco2n_v2": [ 3, 4, 3, 6 ],
    "eco2m": [ 3, 4, 4, 6 ],
}

eos_select = {
    "eos7",
    "eos8",
    "eoswasg",
    "eco2n",
    "eco2n_v2",
    "eco2m",
}

header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"


def new():
    """
    Reset parameter values to default.
    """
    Parameters.update(_Parameters)


def set_parameters(parameters):
    """
    Set parameter values.

    Parameters
    ----------
    parameters : dict
        Input parameter values.
    """
    assert isinstance(parameters, dict)
    Parameters.update(_Parameters)
    Parameters.update(parameters)


def block(keyword, multi = False, noend = False):
    """
    Decorator for block writing functions.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            head_fmt = "{:5}{}" if noend else "{:5}{}\n"
            out = [ head_fmt.format(keyword, header) ]
            out += func(*args, **kwargs)
            out += [ "\n" ] if multi else []
            return out
        return wrapper
    return decorator