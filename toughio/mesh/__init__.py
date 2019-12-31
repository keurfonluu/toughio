# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from . import utils
from . import spatial
from .helpers import (
    read,
    write,
    write_points_cells,
)

from meshio import (
    Mesh,
    __version__,
)
version = tuple(int(i) for i in __version__.split("."))
if version < (3,3,0):
    from meshio import (
        XdmfTimeSeriesReader,
        XdmfTimeSeriesWriter,
    )
else:
    from meshio.xdmf import TimeSeriesReader as XdmfTimeSeriesReader
    from meshio.xdmf import TimeSeriesWriter as XdmfTimeSeriesWriter


__all__ = [
    "read",
    "write",
    "write_points_cells",
    "Mesh",
    "XdmfTimeSeriesReader",
    "XdmfTimeSeriesWriter",
    "utils",
    "spatial",
]