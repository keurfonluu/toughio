from ._csv import read
from .._helpers import register

__all__ = [
    "read",
]


register("csv", read)
