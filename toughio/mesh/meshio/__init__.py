# -*- coding: utf-8 -*-

"""
This directory contains a bundled meshio package that is updated every
once in a while. ToughIO first tries to import the packaged version.

Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

try:
    from meshio import (
        read,
        write,
        write_points_cells,
        Mesh,
        XdmfTimeSeriesReader,
        XdmfTimeSeriesWriter,
    )
except ImportError:
    import sys
    if sys.version_info[0] < 3:
        from .meshio2 import (
            read,
            write,
            write_points_cells,
            Mesh,
            XdmfTimeSeriesReader,
            XdmfTimeSeriesWriter,
        )
    else:
        from .meshio3 import (
            read,
            write,
            write_points_cells,
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
]