# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from .__about__ import (
    __version__,
    __author__,
    __author_email__,
    __website__,
    __license__,
)
from .helpers import (
    read,
    write,
    write_points_cells,
)
from . import utils, spatial
try:
    from meshio import (
        Mesh,
        XdmfTimeSeriesReader,
        XdmfTimeSeriesWriter,
    )
except ImportError:
    from .externals.meshio import (
        Mesh,
        XdmfTimeSeriesReader,
        XdmfTimeSeriesWriter,
    )

__all__ = [
    "read",
    "write",
    "write_points_cells",
    "Mesh",
    "XdmfTimeSeriesReader",
    "XdmfTimeSeriesWriter",
    "utils",
    "spatial",
    "__version__",
    "__author__",
    "__author_email__",
    "__website__",
    "__license__",
]