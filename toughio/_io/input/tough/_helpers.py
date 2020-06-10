from __future__ import division

import logging
from copy import deepcopy
from functools import wraps

import numpy

__all__ = [
    "dtypes",
    "block",
    "check_parameters",
    "read_record",
    "write_record",
    "str2float",
    "prune_nones_dict",
    "prune_nones_list",
]


dtypes = {
    "PARAMETERS": {
        "title": "str",
        "eos": "str",
        "n_component": "int",
        "n_phase": "int",
        "n_component_mass": "int",
        "flac": "dict",
        "isothermal": "bool",
        "start": "bool",
        "nover": "bool",
        "rocks": "dict",
        "rocks_order": "array_like",
        "options": "dict",
        "extra_options": "dict",
        "more_options": "dict",
        "selections": "dict",
        "solver": "dict",
        "generators": "dict",
        "times": "scalar_array_like",
        "element_history": "array_like",
        "connection_history": "array_like",
        "generator_history": "array_like",
        "diffusion": "array_like",
        "output": "dict",
        "elements": "dict",
        "elements_order": "array_like",
        "connections": "dict",
        "connections_order": "array_like",
        "initial_conditions": "dict",
        "initial_conditions_order": "array_like",
        "default": "dict",
    },
    "ROCKS": {
        "density": "scalar",
        "porosity": "scalar",
        "permeability": "scalar_array_like",
        "conductivity": "scalar",
        "specific_heat": "scalar",
        "compressibility": "scalar",
        "expansivity": "scalar",
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
    "FLAC": {"creep": "bool", "porosity_model": "int", "version": "int"},
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
    "SELEC": {"integers": "dict", "floats": "array_like"},
    "SOLVR": {
        "method": "int",
        "z_precond": "str",
        "o_precond": "str",
        "rel_iter_max": "scalar",
        "eps": "scalar",
    },
    "GENER": {
        "name": "str_array_like",
        "type": "str_array_like",
        "times": "scalar_array_like",
        "rates": "scalar_array_like",
        "specific_enthalpy": "scalar_array_like",
        "layer_thickness": "scalar_array_like",
    },
    "OUTPU": {"format": "str", "variables": "dict"},
    "ELEME": {
        "material": "str_int",
        "volume": "scalar",
        "heat_exchange_area": "scalar",
        "permeability_modifier": "scalar",
        "center": "array_like",
    },
    "CONNE": {
        "permeability_direction": "int",
        "nodal_distances": "array_like",
        "interface_area": "scalar",
        "gravity_cosine_angle": "scalar",
        "radiant_emittance_factor": "scalar",
    },
    "INCON": {"porosity": "scalar", "userx": "array_like", "values": "array_like"},
}


str_to_dtype = {
    "int": (int, numpy.int32, numpy.int64),
    "float": (float, numpy.float32, numpy.float64),
    "str": (str,),
    "bool": (bool,),
    "str_int": (str, int, numpy.int32, numpy.int64),
    "array_like": (list, tuple, numpy.ndarray),
    "dict": (dict,),
    "scalar": (int, float, numpy.int32, numpy.int64, numpy.float32, numpy.float64),
    "scalar_array_like": (
        int,
        float,
        list,
        tuple,
        numpy.int32,
        numpy.int64,
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
                        try:
                            for key in keys[1:]:
                                v = v[key]
                                tmp += "['{}']".format(key)
                            _check_parameters(v, tmp)
                        except KeyError:
                            continue
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
        "f": str2float,
        "e": str2float,
    }

    i = 0
    out = []
    for token in fmt.split(","):
        n = int(token[:-1].split(".")[0])
        tmp = data[i : i + n]
        tmp = tmp if token[-1] == "S" else tmp.strip()
        out.append(token_to_type[token[-1]](tmp) if tmp else None)
        i += n

    return out


def write_record(data, fmt, multi=False):
    """Return a list of record strings given format."""

    def to_str(x, fmt):
        x = "" if x is None else x
        return (
            fmt.format(x)
            if not isinstance(x, str)
            else fmt.replace("g", "").replace("e", "").format(x)
        )

    if not multi:
        data = [to_str(d, f) for d, f in zip(data, fmt)]
        out = ["{:80}\n".format("".join(data))]
    else:
        n = len(data)
        ncol = len(fmt)
        data = [
            data[ncol * i : min(ncol * i + ncol, n)]
            for i in range(int(numpy.ceil(n / ncol)))
        ]

        out = []
        for d in data:
            d = [to_str(dd, f) for dd, f in zip(d, fmt)]
            out += ["{:80}\n".format("".join(d))]

    return out


def str2float(s):
    """Convert variable string to float."""
    try:
        return float(s)
    except ValueError:
        # It's probably something like "0.0001-001"
        significand, exponent = s[:-4], s[-4:]
        return float("{}e{}".format(significand, exponent))


def prune_nones_dict(data):
    """Remove None key/value pairs from dict."""
    return {k: v for k, v in data.items() if v is not None}


def prune_nones_list(data):
    """Remove trailing None values from list."""
    return [x for i, x in enumerate(data) if any(xx is not None for xx in data[i:])]
