from ._tecplot import read, write
from .._helpers import register

__all__ = ["read", "write"]


register("tecplot", [".dat", ".tec"], read, {"tecplot": write})
