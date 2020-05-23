from ._tough import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("tough", [], read, {"tough": write})
