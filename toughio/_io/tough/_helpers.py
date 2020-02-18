import logging
from copy import deepcopy
from functools import wraps

import numpy

__all__ = [
    "dtypes",
    "block",
    "check_parameters",
]


dtypes = {
    "PARAMETERS": {
        "title": "str",
        "eos": "str",
        "n_component": "int",
        "n_phase": "int",
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
        "b_coeff": "scalar",
        "xkd3": "scalar",
        "xkd4": "scalar",
        "incon": "array_like",
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
    """
    Decorator for block writing functions.
    """

    def decorator(func):
        from .._common import header

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
    """
    Decorator to check input parameters.
    """

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
            assert v is None or isinstance(
                v, input_type
            ), "Invalid type for parameter '{}' {}(expected {}).".format(
                k, "in {} ".format(keys) if keys else "", input_types[k],
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
