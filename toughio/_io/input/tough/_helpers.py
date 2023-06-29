from functools import wraps

import numpy as np

from ...._common import prune_values
from ..._common import read_record, write_record


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
