from .._helpers import register
from ._column import read

__all__ = [
    "read",
]


register("column", [".col"], read)
