import meshio

from ._common import get_meshio_version
from ._helpers import read, write, write_points_cells
from ._mesh import Mesh, from_meshio

if get_meshio_version() < (3, 3, 0):
    from meshio import XdmfTimeSeriesReader as TimeSeriesReader
    from meshio import XdmfTimeSeriesWriter as TimeSeriesWriter
else:
    from meshio.xdmf import TimeSeriesReader
    from meshio.xdmf import TimeSeriesWriter


__all__ = [
    "read",
    "write",
    "write_points_cells",
    "Mesh",
    "TimeSeriesReader",
    "TimeSeriesWriter",
    "from_meshio",
]
