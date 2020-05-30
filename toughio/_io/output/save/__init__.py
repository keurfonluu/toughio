from .._helpers import register
from ._save import read

__all__ = [
    "read",
]


register("save", [], read)
