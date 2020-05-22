from ._tecplot import read
from .._helpers import register

__all__ = [
    "read",
]


register("tecplot", [".tec"], read)
