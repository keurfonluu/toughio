from functools import wraps


def section(header, footer="*"):
    """Decorate section writing functions."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            out = [f"{header}"]
            out += func(*args, **kwargs)
            out += [f"{footer}"]

            return out

        return wrapper

    return decorator
