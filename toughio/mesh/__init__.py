# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

import meshio

from . import utils
from . import spatial
from .helpers import (
    read,
    write,
    write_points_cells,
)
from ._mesh import Mesh
from ._common import get_meshio_version

if get_meshio_version() < (3,3,0):
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