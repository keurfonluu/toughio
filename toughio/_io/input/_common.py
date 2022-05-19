import logging

from .._common import to_str


def getval(parameters, keys, default):
    """Get key in parameters dict or return default value."""
    try:
        if isinstance(keys, str):
            return parameters[keys]

        else:
            value = parameters
            for key in keys:
                value = value[key]

            return value

    except KeyError:
        key_str = (
            "'{}'".format(keys)
            if isinstance(keys, str)
            else "".join(f"['{key}']" for key in keys)
        )
        logging.warning(f"Key {key_str} is not defined. Setting to {default}.")

        return default


def write_ffrecord(values, verbose=False, int_fmt="{:4d}", float_fmt="{{:9f}}", str_fmt="{:20}"):
    """Write free-format record."""
    return [(
        f"{' '.join(to_str(value, int_fmt if isinstance(value, int) else float_fmt if isinstance(value, float) else str_fmt) for value in values)}"
        if verbose
        else f"{' '.join(str(x) for x in values)}"
    )]
