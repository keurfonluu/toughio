from ._column import read
from .._helpers import register


__all__ = [
    "read",
]


register("column", [".col"], read)
