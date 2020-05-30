from .._helpers import register
from ._tough import read

__all__ = [
    "read",
]


register("tough", [], read)
