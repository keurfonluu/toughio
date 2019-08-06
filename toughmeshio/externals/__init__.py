# -*- coding: utf-8 -*-

"""
This directory contains a bundled meshio package that is updated every
once in a while. ToughMeshio first tries to import the packaged version.

Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

import sys
if sys.version_info[0] < 3:
    from . import meshio2 as meshio
else:
    from . import meshio

__all__ = [
    "meshio",
]