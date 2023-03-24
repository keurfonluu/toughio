from .._helpers import register
from ._csv import read

__all__ = [
    "read",
]


register("csv", [".csv"], read)
