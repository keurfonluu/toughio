import logging

from ..._common import prune_values
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
            f"'{keys}'"
            if isinstance(keys, str)
            else "".join(f"['{key}']" for key in keys)
        )
        logging.warning(f"Key {key_str} is not defined. Setting to {default}.")

        return default


def write_ffrecord(
    values,
    verbose=False,
    fmt=None,
    int_fmt="{:4d}",
    float_fmt="{{:9f}}",
    str_fmt="{:20}",
    end="",
):
    """Write free-format record."""
    if verbose:
        if fmt:
            values = [to_str(value, f) for value, f, in zip(values, fmt)]
            return [f"{' '.join(values)}{end}"]

        else:
            return [
                f"{' '.join(to_str(value, int_fmt if isinstance(value, int) else float_fmt if isinstance(value, float) else str_fmt) for value in values)}{end}"
            ]

    else:
        return [f"{' '.join(str(x) for x in values)}{end}"]


def read_end_comments(fiter):
    # Save end comments
    end_comments = []
    while True:
        try:
            end_comments.append(fiter.next().rstrip())

        except StopIteration:
            break

    # Remove trailing empty records
    end_comments = [comment if comment else None for comment in end_comments]
    end_comments = prune_values(end_comments)
    if end_comments:
        return (
            end_comments[0]
            if len(end_comments) == 1
            else [comment if comment else "" for comment in end_comments]
        )

    else:
        return None
