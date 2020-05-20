from ._csv import read, write
from .._helpers import register

__all__ = [
    "read",
    "write",
]


register("csv", read, write)
