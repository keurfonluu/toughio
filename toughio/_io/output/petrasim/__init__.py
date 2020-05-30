from .._helpers import register
from ._petrasim import read, write

__all__ = [
    "read",
    "write",
]


register("petrasim", [], read, write)
