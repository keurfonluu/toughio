from ._flac3d import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("flac3d", [".f3grid"], read, {"flac3d": write})
