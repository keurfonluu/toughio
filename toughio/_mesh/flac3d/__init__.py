from .._helpers import register
from ._flac3d import read, write

__all__ = [
    "read",
    "write",
]


register("flac3d", [".f3grid"], read, write)
