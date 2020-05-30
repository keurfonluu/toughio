from .._helpers import register
from ._csv import read, write

__all__ = [
    "read",
    "write",
]


register("csv", [".csv"], read, write)
