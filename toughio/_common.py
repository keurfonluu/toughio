import os
import warnings
from functools import wraps

__all__ = [
    "deprecated",
    "filetype_from_filename",
]


def deprecated(version=None, extra_msg=None):
    """Decorate deprecated functions."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warn_msg = "Function '{}' will be deprecated".format(func.__name__)
            warn_msg += " in version '{}'.".format(version) if version else "."
            warn_msg += " {}".format(extra_msg) if extra_msg else ""
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(warn_msg, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter("default", DeprecationWarning)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def filetype_from_filename(filename, extension_to_filetype):
    """Determine file type from its extension."""
    ext = os.path.splitext(filename)[1].lower()

    return extension_to_filetype[ext] if ext in extension_to_filetype.keys() else ""
