from .._helpers import register
from ._avsucd import read, write

__all__ = [
    "read",
    "write",
]


register("avsucd", [], read, write)
