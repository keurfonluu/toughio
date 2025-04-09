from ._read import read
from ._write import write
from .._helpers import register


__all__ = [
    "read",
    "write",
]


register("toughreact-solute", [], read, write)
