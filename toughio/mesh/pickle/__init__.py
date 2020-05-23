from ._pickle import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("pickle", [".pickle", ".pkl"], read, {"pickle": write})
