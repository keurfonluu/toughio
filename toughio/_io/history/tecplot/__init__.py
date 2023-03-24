from .._helpers import register
from ._tecplot import read

__all__ = [
    "read",
]


register("tecplot", [".tec"], read)
