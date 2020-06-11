from .._helpers import register
from ._tough import read, write

__all__ = [
    "read",
    "write",
]


register("tough", [], read, write)
