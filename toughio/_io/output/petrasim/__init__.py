from ._petrasim import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("petrasim", [], read, write)
