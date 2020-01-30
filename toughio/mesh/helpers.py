# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from ._mesh import Mesh, _meshio_to_toughio_mesh
from . import tough
from . import flac3d_io
from . import eclipse_io
import meshio

__all__ = [
    "read",
    "write",
    "write_points_cells",
]


_extension_to_filetype = {
    ".f3grid": "flac3d",
    ".grdecl": "eclipse",
}


def _filetype_from_filename(filename):
    """
    Determine file type from its extension.
    """
    import os
    ext = os.path.split(filename)[1].split(".")[-1]
    try:
        return _extension_to_filetype[".{}".format(ext.lower())]
    except KeyError:
        return ""


def read(filename, file_format = None, **kwargs):
    """
    Read unstructured mesh from file.

    Parameters
    ----------
    filename : str
        Input file name.
    file_format : str or None, optional, default None
        Input file format. If `None`, it will be guessed from file's
        extension.

    Other Parameters
    ----------------
    repair_conformity : bool, optional, default False
        Only if ``file_format == 'eclipse'``. Repair mesh conformity
        (reconnect adjacent cells) by splitting bricks as smaller bricks.
    repair_cells : bool, optional, default False
        Only if ``file_format == 'eclipse'``. Convert bricks as hexahedra,
        wedges, pyramids or tetrahedra depending on the number of unique
        points. Repaired mesh may be semi-conformal (i.e. at least one
        cell completely shares its face with its neighbor).
    z_precision : int or None, optional, default None
        Only if ``file_format == 'eclipse'``. If not `None`, round corner
        depths to z_precision decimal points (only if ``repair_conformity == True``).
    invert_zaxis: bool, optional, default False
        Only if ``file_format == 'eclipse'``. If `True`, invert Z axis by
        multiplying Z coordinates by -1.

    Returns
    -------
    Mesh
        Imported mesh.

    Note
    ----
    This function wraps function ``meshio.read`` by adding support to
    Eclipse GRDECL and FLAC3D grids. Therefore, all the formats compatible
    with ``meshio`` are also supported.
    """
    # Check file format
    assert isinstance(filename, str)
    fmt = file_format if file_format else _filetype_from_filename(filename)

    # Call custom readers for TOUGH, FLAC3D and Eclipse
    format_to_reader = {
        "tough": ( tough, (), {} ),
        "flac3d": ( flac3d_io, (), {} ),
        "flac3d-ascii": ( flac3d_io, (), {} ),
        "eclipse": (
            eclipse_io, (),
            {
                "repair_conformity": False,
                "repair_cells": False,
                "z_precision": None,
                "invert_zaxis": False,
            },
        ),
    }
    if fmt in format_to_reader.keys():
        interface, args, default_kwargs = format_to_reader[fmt]
        _kwargs = default_kwargs.copy()
        _kwargs.update(kwargs)
        mesh = interface.read(filename, *args, **_kwargs)
    else:
        mesh = meshio.read(filename, file_format)
    return _meshio_to_toughio_mesh(mesh)


def write(filename, mesh, file_format = None, **kwargs):
    """
    Write unstructured mesh to file.

    Parameters
    ----------
    filename : str
        Output file name.
    mesh : Mesh
        Mesh to export.
    file_format : str or None, optional, default None
        Output file format. If `None`, it will be guessed from file's
        extension. To write TOUGH MESH, `file_format` must be specified
        as 'tough' (no specific extension exists for TOUGH MESH).

    Other Parameters
    ----------------
    rotation_angle : float, optional, default 0.
        Only if ``file_format == 'tough'``. Angle to rotate cell
        connection line for calculation of angle with gravity force.

    Note
    ----
    This function wraps functions ``meshio.write`` by adding support to
    TOUGH and FLAC3D grids. Therefore, all the formats compatible with
    ``meshio`` are also supported.
    """
    # Check file format
    assert isinstance(filename, str)
    fmt = file_format if file_format else _filetype_from_filename(filename)

    # Call custom writer for TOUGH, FLAC3D and Eclipse
    format_to_writer = {
        "tough": (
            tough, (),
            {
                "rotation_angle": 0.,
            },
        ),
        "flac3d": ( flac3d_io, (), {} ),
        "flac3d-ascii": ( flac3d_io, (), {} ),
        "eclipse": ( eclipse_io, (), {} ),
    }
    if fmt in format_to_writer.keys():
        interface, args, default_kwargs = format_to_writer[fmt]
        _kwargs = default_kwargs.copy()
        _kwargs.update(kwargs)
        interface.write(filename, mesh, *args, **_kwargs)
    else:
        mesh = mesh.to_meshio()
        meshio.write(filename, mesh, file_format = file_format, **kwargs)


def write_points_cells(filename, points, cells, point_data = None,
    cell_data = None, field_data = None, file_format = None, **kwargs):
    """
    Write unstructured mesh to file given points and cells data.

    Parameters
    ----------
    filename : str
        Output file name.
    points : ndarray
        Grid points array.
    cells : dict
        Grid cell data.
    point_data : dict or None, optional, default None
        Data associated to grid points.
    cell_data : dict or None, optional, default None
        Data associated to grid cells.
    field_data : dict or None, optional, default None
        Data names.
    file_format : str or None, optional, default None
        Output file format. If `None`, it will be guessed from file's
        extension. To write TOUGH MESH, `file_format` must be specified
        as 'tough' (no specific extension exists for TOUGH MESH).

    Other Parameters
    ----------------
    kwargs : dict
        Refer to function ``write`` for additional information.
    """
    mesh = Mesh(
        points = points,
        cells = cells,
        point_data = point_data,
        cell_data = cell_data,
        field_data = field_data,
    )
    write(filename, mesh, file_format = file_format, **kwargs)