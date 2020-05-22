from ._save import read
from .._helpers import register

__all__ = [
    "read",
]


register("save", [], read)
