from ._avsucd import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("avsucd", [], read, {"avsucd": write})
