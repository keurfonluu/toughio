from .._helpers import register
from ._tecplot import read, write

__all__ = [
    "read",
    "write",
]


register("tecplot", [".tec"], read, write)
