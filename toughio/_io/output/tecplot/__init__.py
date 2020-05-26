from ._tecplot import read, write
from .._helpers import register

__all__ = [
    "read",
]


register("tecplot", [".tec"], read, write)
