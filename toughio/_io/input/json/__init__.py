from ._json import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("json", [".json"], read, {"json": write})
