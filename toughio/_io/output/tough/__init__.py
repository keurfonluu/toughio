from ._tough import read
from .._helpers import register

__all__ = [
    "read",
]


register("tough", read)
