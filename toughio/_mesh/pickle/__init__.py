from .._helpers import register
from ._pickle import read, write

__all__ = [
    "read",
    "write",
]


register("pickle", [".pickle", ".pkl"], read, write)
