import warnings
from functools import wraps

__all__ = [
    "deprecated"
]


def deprecated(version=None, extra_msg=None):
    """Decorate deprecated functions."""

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            warn_msg = "Function '{}' will be deprecated".format(func.__name__)
            warn_msg += (
                " in version '{}'.".format(version)
                if version
                else "."
            )
            warn_msg += " {}".format(extra_msg) if extra_msg else ""
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                warn_msg,
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)

            return func(*args, **kwargs)

        return wrapper

    return decorator
