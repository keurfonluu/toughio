import logging
from copy import deepcopy
from functools import wraps

import numpy

__all__ = [
    "dtypes",
    "block",
    "check_parameters",
    "read_record",
    "prune_nones_dict",
    "prune_nones_list",
]


dtypes = {
    "PARAMETERS": {
        "title": "str",
        "eos": "str",
        "version": "int",
        "n_component": "int",
        "n_phase": "int",
        "n_component_mass": "int",
        "flac": "bool",
        "creep": "bool",
        "porosity_model": "int",
        "isothermal": "bool",
        "start": "bool",
        "nover": "bool",
        "endfi": "bool",
        "rocks": "dict",
        "rocks_order": "array_like",
        "options": "dict",
        "extra_options": "dict",
        "more_options": "dict",
        "selections": "dict",
        "extra_selections": "array_like",
        "solver": "dict",
        "generators": "dict",
        "times": "scalar_array_like",
        "element_history": "array_like",
        "connection_history": "array_like",
        "generator_history": "array_like",
        "diffusion": "array_like",
        "output": "dict",
        "default": "dict",
    },
    "ROCKS": {
        "density": "scalar",
        "porosity": "scalar",
        "permeability": "scalar_array_like",
        "conductivity": "scalar",
        "specific_heat": "scalar",
        "compressibility": "scalar",
        "expansion": "scalar",
        "conductivity_dry": "scalar",
        "tortuosity": "scalar",
        "klinkenberg_parameter": "scalar",
        "distribution_coefficient_3": "scalar",
        "distribution_coefficient_4": "scalar",
        "initial_condition": "array_like",
        "relative_permeability": "dict",
        "capillarity": "dict",
        "permeability_model": "dict",
        "equivalent_pore_pressure": "dict",
    },
    "MODEL": {"id": "int", "parameters": "array_like"},
    "PARAM": {
        "n_iteration": "int",
        "n_cycle": "int",
        "n_second": "int",
        "n_cycle_print": "int",
        "verbosity": "int",
        "temperature_dependence_gas": "scalar",
        "effective_strength_vapor": "scalar",
        "t_ini": "scalar",
        "t_max": "scalar",
        "t_steps": "scalar_array_like",
        "t_step_max": "scalar",
        "t_reduce_factor": "scalar",
        "gravity": "scalar",
        "mesh_scale_factor": "scalar",
        "eps1": "scalar",
        "eps2": "scalar",
        "w_upstream": "scalar",
        "w_newton": "scalar",
        "derivative_factor": "scalar",
    },
    "MOP": {i + 1: "int" for i in range(24)},
    "MOMOP": {i + 1: "int" for i in range(40)},
    "SELEC": {i + 1: "int" for i in range(16)},
    "SOLVR": {
        "method": "int",
        "z_precond": "str",
        "o_precond": "str",
        "rel_iter_max": "scalar",
        "eps": "scalar",
    },
    "GENER": {
        "type": "str_array_like",
        "times": "scalar_array_like",
        "rates": "scalar_array_like",
        "specific_enthalpy": "scalar_array_like",
        "layer_thickness": "scalar_array_like",
    },
    "OUTPU": {"format": "str", "variables": "dict"},
}


str_to_dtype = {
    "int": (int, numpy.int32),
    "float": (float, numpy.float32, numpy.float64),
    "str": (str,),
    "bool": (bool,),
    "array_like": (list, tuple, numpy.ndarray),
    "dict": (dict,),
    "scalar": (int, float, numpy.int32, numpy.float32, numpy.float64),
    "scalar_array_like": (
        int,
        float,
        list,
        tuple,
        numpy.int32,
        numpy.float32,
        numpy.float64,
        numpy.ndarray,
    ),
    "str_array_like": (str, list, tuple, numpy.ndarray),
}


def block(keyword, multi=False, noend=False):
    """Decorate block writing functions."""

    def decorator(func):
        from ._common import header

        @wraps(func)
        def wrapper(*args, **kwargs):
            head_fmt = "{:5}{}" if noend else "{:5}{}\n"
            out = [head_fmt.format(keyword, header)]
            out += func(*args, **kwargs)
            out += ["\n"] if multi else []

            return out

        return wrapper

    return decorator


def check_parameters(input_types, keys=None, is_list=False):
    """Decorate function to check input parameters."""

    def _check_parameters(params, keys=None):
        for k, v in params.items():
            # Check whether parameters contain unknown keys
            # Log error if it does and skip
            if k not in input_types.keys():
                logging.warning(
                    "Unknown key '{}'{}. Skipping.".format(
                        k, " in {}".format(keys) if keys else ""
                    )
                )
                continue

            # Check input types
            input_type = str_to_dtype[input_types[k]]
            if not (v is None or isinstance(v, input_type)):
                raise TypeError(
                    "Invalid type for parameter '{}' {}(expected {}).".format(
                        k, "in {} ".format(keys) if keys else "", input_types[k],
                    )
                )

    keys = [keys] if isinstance(keys, str) else keys

    def decorator(func):
        @wraps(func)
        def wrapper(parameters):
            if not keys:
                _check_parameters(parameters)
            else:
                params = deepcopy(parameters[keys[0]])
                keys_str = "['{}']".format(keys[0])
                if is_list:
                    for k, v in params.items():
                        tmp = keys_str
                        tmp += "['{}']".format(k)
                        for key in keys[1:]:
                            v = v[key]
                            tmp += "['{}']".format(key)
                        _check_parameters(v, tmp)
                else:
                    for key in keys[1:]:
                        params = params[key]
                        keys_str += "['{}']".format(key)
                    _check_parameters(params, keys_str)

            out = func(parameters)

            return out

        return wrapper

    return decorator


def read_record(data, fmt):
    """Parse string to data given format."""
    token_to_type = {
        "s": str,
        "S": str,
        "d": int,
        "f": float,
        "e": float,
    }
    
    i = 0
    out = []
    for token in fmt.split(","):
        n = int(token[:-1])
        tmp = data[i:i+n]
        tmp = tmp if token[-1] == "S" else tmp.strip()
        out.append(token_to_type[token[-1]](tmp) if tmp else None)
        i += n

    return out


def prune_nones_dict(data):
    """Remove None key/value pairs from dict."""
    return {k: v for k, v in data.items() if v is not None}


def prune_nones_list(data):
    """Remove trailing None values from list."""
    return [x for i, x in enumerate(data) if any(xx is not None for xx in data[i:])]
