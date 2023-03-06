import logging
from copy import deepcopy
from functools import wraps

import numpy as np

from ...._common import prune_values
from ..._common import read_record, write_record

dtypes = {
    "PARAMETERS": {
        "title": "str_array_like",
        "eos": "str",
        "n_component": "int",
        "n_phase": "int",
        "do_diffusion": "bool",
        "n_component_incon": "int",
        "react": "dict",
        "flac": "dict",
        "chemical_properties": "dict",
        "non_condensible_gas": "str_array_like",
        "isothermal": "bool",
        "start": "bool",
        "nover": "bool",
        "rocks": "dict",
        "options": "dict",
        "extra_options": "dict",
        "more_options": "dict",
        "selections": "dict",
        "solver": "dict",
        "generators": "array_like",
        "boundary_conditions": "array_like",
        "times": "array_like",
        "hysteresis_options": "dict",
        "element_history": "array_like",
        "connection_history": "array_like",
        "generator_history": "array_like",
        "diffusion": "array_like",
        "output": "dict",
        "elements": "dict",
        "coordinates": "bool",
        "connections": "dict",
        "initial_conditions": "dict",
        "meshmaker": "dict",
        "poiseuille": "dict",
        "default": "dict",
        "array_dimensions": "dict",
        "end_comments": "str_array_like",
    },
    "DIMEN": {
        "n_rocks": "int",
        "n_times": "int",
        "n_generators": "int",
        "n_rates": "int",
        "n_increment_x": "int",
        "n_increment_y": "int",
        "n_increment_z": "int",
        "n_increment_rad": "int",
        "n_properties": "int",
        "n_properties_times": "int",
        "n_regions": "int",
        "n_regions_parameters": "int",
        "n_ltab": "int",
        "n_rpcap": "int",
        "n_elements_timbc": "int",
        "n_timbc": "int",
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
        "tortuosity_exponent": "scalar",
        "porosity_crit": "scalar",
        "initial_condition": "array_like",
        "relative_permeability": "dict",
        "capillarity": "dict",
        "react_tp": "dict",
        "react_hcplaw": "dict",
        "permeability_model": "dict",
        "equivalent_pore_pressure": "dict",
        "phase_composition": "int",
    },
    "FLAC": {"creep": "bool", "porosity_model": "int", "version": "int"},
    "CHEMP": {
        "temperature_crit": "scalar",
        "pressure_crit": "scalar",
        "compressibility_crit": "scalar",
        "pitzer_factor": "scalar",
        "dipole_moment": "scalar",
        "boiling_point": "scalar",
        "vapor_pressure_a": "scalar",
        "vapor_pressure_b": "scalar",
        "vapor_pressure_c": "scalar",
        "vapor_pressure_d": "scalar",
        "molecular_weight": "scalar",
        "heat_capacity_a": "scalar",
        "heat_capacity_b": "scalar",
        "heat_capacity_c": "scalar",
        "heat_capacity_d": "scalar",
        "napl_density_ref": "scalar",
        "napl_temperature_ref": "scalar",
        "gas_diffusivity_ref": "scalar",
        "gas_temperature_ref": "scalar",
        "exponent": "scalar",
        "napl_viscosity_a": "scalar",
        "napl_viscosity_b": "scalar",
        "napl_viscosity_c": "scalar",
        "napl_viscosity_d": "scalar",
        "volume_crit": "scalar",
        "solubility_a": "scalar",
        "solubility_b": "scalar",
        "solubility_c": "scalar",
        "solubility_d": "scalar",
        "oc_coeff": "scalar",
        "oc_fraction": "scalar",
        "oc_decay": "scalar",
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
        "react_wdata": "array_like",
    },
    "MOP": {i + 1: "int" for i in range(24)},
    "MOPR": {i + 1: "int" for i in range(25)},
    "MOMOP": {i + 1: "int" for i in range(50)},
    "HYSTE": {i + 1: "int" for i in range(3)},
    "SELEC": {"integers": "dict", "floats": "array_like"},
    "SOLVR": {
        "method": "int",
        "z_precond": "str",
        "o_precond": "str",
        "rel_iter_max": "scalar",
        "eps": "scalar",
    },
    "GENER": {
        "label": "str",
        "name": "str",
        "nseq": "scalar",
        "nadd": "scalar",
        "nads": "scalar",
        "type": "str",
        "times": "scalar_array_like",
        "rates": "scalar_array_like",
        "specific_enthalpy": "scalar_array_like",
        "layer_thickness": "scalar",
        "n_layer": "int",
        "conductivity_times": "array_like",
        "conductivity_factors": "array_like",
    },
    "TIMBC": {
        "label": "str",
        "variable": "int",
        "times": "scalar_array_like",
        "values": "scalar_array_like",
    },
    "OUTPT": {"format": "int", "shape": "array_like"},
    "OUTPU": {"format": "str", "variables": "array_like"},
    "ELEME": {
        "nseq": "int",
        "nadd": "int",
        "material": "str_int",
        "volume": "scalar",
        "heat_exchange_area": "scalar",
        "permeability_modifier": "scalar",
        "center": "array_like",
    },
    "CONNE": {
        "nseq": "int",
        "nadd": "array_like",
        "permeability_direction": "int",
        "nodal_distances": "array_like",
        "interface_area": "scalar",
        "gravity_cosine_angle": "scalar",
        "radiant_emittance_factor": "scalar",
    },
    "INCON": {
        "porosity": "scalar",
        "userx": "array_like",
        "values": "array_like",
        "phase_composition": "int",
        "permeability": "scalar_array_like",
    },
    "MESHM": {"type": "str", "parameters": "array_like", "angle": "scalar"},
    "POISE": {
        "start": "array_like",
        "end": "array_like",
        "aperture": "scalar",
    },
}


str_to_dtype = {
    "int": (int, np.int32, np.int64),
    "float": (float, np.float32, np.float64),
    "str": (str,),
    "bool": (bool,),
    "str_int": (str, int, np.int32, np.int64),
    "array_like": (list, tuple, np.ndarray),
    "dict": (dict,),
    "scalar": (int, float, np.int32, np.int64, np.float32, np.float64),
    "scalar_array_like": (
        int,
        float,
        list,
        tuple,
        np.int32,
        np.int64,
        np.float32,
        np.float64,
        np.ndarray,
    ),
    "str_array_like": (str, list, tuple, np.ndarray),
}


def block(keyword, multi=False, noend=False):
    """Decorate block writing functions."""

    def decorator(func):
        from ._common import header

        @wraps(func)
        def wrapper(*args, **kwargs):
            head = f"{keyword:5}{header}"
            out = [head if noend else f"{head}\n"]
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
            if k not in input_types:
                logging.warning(
                    f"Unknown key '{k}'{f' in {keys}' if keys else ''}. Skipping."
                )
                continue

            # Check input types
            input_type = str_to_dtype[input_types[k]]
            if not (v is None or isinstance(v, input_type)):
                raise TypeError(
                    f"Invalid type for parameter '{k}'{f' in {keys}' if keys else ''} (expected {input_types[k]})."
                )

    keys = [keys] if isinstance(keys, str) else keys

    def decorator(func, *args, **kwargs):
        @wraps(func)
        def wrapper(parameters, *args, **kwargs):
            if not keys:
                _check_parameters(parameters)

            else:
                params = deepcopy(parameters[keys[0]])
                keys_str = f"['{keys[0]}']"
                if is_list:
                    if isinstance(params, dict):
                        for k, v in params.items():
                            tmp = keys_str
                            tmp += f"['{k}']"

                            try:
                                for key in keys[1:]:
                                    v = v[key]
                                    tmp += f"['{key}']"
                                _check_parameters(v, tmp)

                            except KeyError:
                                continue
                    else:
                        for i, param in enumerate(params):
                            tmp = f"{keys_str}[{i}]"
                            _check_parameters(param, tmp)

                else:
                    for key in keys[1:]:
                        params = params[key]
                        keys_str += f"['{key}']"

                    _check_parameters(params, keys_str)

            out = func(parameters, *args, **kwargs)

            return out

        return wrapper

    return decorator


def read_model_record(line, fmt, i=2):
    """Read model record defined by 'id' and 'parameters'."""
    data = read_record(line, fmt)

    return {
        "id": data[0],
        "parameters": prune_values(data[i:]),
    }


def write_model_record(data, key, fmt):
    """Write model record defined by 'id' and 'parameters'."""
    if key in data:
        values = [data[key]["id"], None]
        values += list(data[key]["parameters"])
        return write_record(values, fmt)

    else:
        return write_record([], [])


def read_primary_variables(f, fmt, n_variables):
    """Read primary variables."""
    data = []

    if n_variables:
        n = int(np.ceil(n_variables / 4))

        for _ in range(n):
            line = f.next()
            data += read_record(line, fmt)

    else:
        while True:
            i = f.tell()
            line = f.next()

            if line.strip():
                try:
                    data += read_record(line, fmt)

                except ValueError:
                    break

            else:
                break

        f.seek(i, increment=-1)

    return data
