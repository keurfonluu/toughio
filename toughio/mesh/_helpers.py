import meshio

from . import avsucd, flac3d, pickle, tecplot, tough
from ._mesh import Mesh, from_meshio

__all__ = [
    "read",
    "write",
    "write_points_cells",
]


_extension_to_filetype = {
    ".dat": "tecplot",
    ".f3grid": "flac3d",
    ".pickle": "pickle",
}


def _filetype_from_filename(filename):
    """Determine file type from its extension.
    """
    import os

    ext = os.path.splitext(filename)[1].lower()
    return _extension_to_filetype[ext] if ext in _extension_to_filetype.keys() else ""


def read(filename, file_format=None, **kwargs):
    """Read unstructured mesh from file.

    Parameters
    ----------
    filename : str
        Input file name.
    file_format : str or None, optional, default None
        Input file format.

    Returns
    -------
    toughio.Mesh
        Imported mesh.
    """
    # Check file format
    assert isinstance(filename, str)
    fmt = file_format if file_format else _filetype_from_filename(filename)

    # Call custom readers
    format_to_reader = {
        "tough": (tough, (), {}),
        "avsucd": (avsucd, (), {}),
        "flac3d": (flac3d, (), {}),
        "pickle": (pickle, (), {}),
        "tecplot": (tecplot, (), {}),
    }
    if fmt in format_to_reader.keys():
        interface, args, default_kwargs = format_to_reader[fmt]
        _kwargs = default_kwargs.copy()
        _kwargs.update(kwargs)
        return interface.read(filename, *args, **_kwargs)
    else:
        mesh = meshio.read(filename, file_format)
        return from_meshio(mesh)


def write(filename, mesh, file_format=None, **kwargs):
    """Write unstructured mesh to file.

    Parameters
    ----------
    filename : str
        Output file name.
    mesh : toughio.Mesh
        Mesh to export.
    file_format : str or None, optional, default None
        Output file format.

    Other Parameters
    ----------------
    nodal_distance : str ('line' or 'orthogonal'), optional, default 'line'
        Only if ``file_format = "tough"``. Method to calculate connection
        nodal distances:
        - 'line': distance between node and common face along connecting
        line (distance is not normal),
        - 'orthogonal' : distance between node and its orthogonal
        projection onto common face (shortest distance).
    material_name : dict or None, default None
        Only if ``file_format = "tough"``. Rename cell material.
    material_end : str, array_like or None, default None
        Only if ``file_format = "tough"``. Move cells to bottom of block
        'ELEME' if their materials is in `material_end`.
    incon_eos : str or None, optional, default None
        Equation-of-state identifier to determine the actual number of
        primary variables to initialize. If `None`, TOUGH input `INCON`
        file will not be written.
    """
    # Check file format
    assert isinstance(filename, str)
    fmt = file_format if file_format else _filetype_from_filename(filename)

    # Call custom writer
    format_to_writer = {
        "tough": (
            tough,
            (),
            {
                "nodal_distance": "line",
                "material_name": None,
                "material_end": None,
                "incon_eos": None,
            },
        ),
        "avsucd": (avsucd, (), {}),
        "flac3d": (flac3d, (), {}),
        "pickle": (pickle, (), {}),
        "tecplot": (tecplot, (), {}),
    }
    if fmt in format_to_writer.keys():
        interface, args, default_kwargs = format_to_writer[fmt]
        _kwargs = default_kwargs.copy()
        _kwargs.update(kwargs)
        interface.write(filename, mesh, *args, **_kwargs)
    else:
        mesh = mesh.to_meshio()
        meshio.write(filename, mesh, file_format=file_format, **kwargs)


def write_points_cells(
    filename,
    points,
    cells,
    point_data=None,
    cell_data=None,
    field_data=None,
    file_format=None,
    **kwargs
):
    """Write unstructured mesh to file given points and cells data.

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
        Output file format.

    Other Parameters
    ----------------
    kwargs : dict
        Refer to function ``write`` for additional information.
    """
    mesh = Mesh(
        points=points,
        cells=cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
    )
    write(filename, mesh, file_format=file_format, **kwargs)
