import pathlib
from copy import deepcopy

import meshio
import numpy as np

from .._common import filetype_from_filename, register_format
from ._mesh import from_meshio

__all__ = [
    "register",
    "read",
    "write",
    "read_time_series",
    "write_time_series",
]


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}


def register(file_format, extensions, reader, writer=None):
    """
    Register a new mesh format.

    Parameters
    ----------
    file_format : str
        File format to register.
    extensions : array_like
        List of extensions to associate to the new format.
    reader : callable
        Read fumction.
    writer : callable or None, optional, default None
        Write function.

    """
    register_format(
        fmt=file_format,
        ext_to_fmt=_extension_to_filetype,
        reader_map=_reader_map,
        writer_map=_writer_map,
        extensions=extensions,
        reader=reader,
        writer=writer,
    )


def get_material_key(cell_data):
    """Get key of material data in cell_data."""
    from meshio._common import _pick_first_int_data

    key, _ = _pick_first_int_data(cell_data)

    return key


def read(filename, file_format=None, **kwargs):
    """
    Read unstructured mesh from file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_format : str or None, optional, default None
        Input file format.

    Other Parameters
    ----------------
    label_length : int or None, optional, default None
        Only if ``file_format = "tough"``. Number of characters in cell labels.

    Returns
    -------
    toughio.Mesh
        Imported mesh.

    """
    # Check file format
    fmt = (
        file_format
        if file_format
        else filetype_from_filename(filename, _extension_to_filetype)
    )

    # Call custom readers
    if fmt in _reader_map:
        mesh = _reader_map[fmt](filename, **kwargs)
        if fmt not in {"tough", "pickle"}:
            mesh.cell_data = {k: np.concatenate(v) for k, v in mesh.cell_data.items()}
            key = get_material_key(mesh.cell_data)
            if key:
                mesh.cell_data["material"] = mesh.cell_data.pop(key)
    else:
        mesh = meshio.read(filename, file_format)
        mesh = from_meshio(mesh)

    # Remove lower order cells
    if not isinstance(mesh, dict):
        idx = np.ones(len(mesh.cells), dtype=bool)

        celltypes = np.array([cell.type for cell in mesh.cells])
        cell_data = {k: mesh.split(v) for k, v in mesh.cell_data.items()}

        idx = np.logical_and(idx, celltypes != "vertex")
        idx = np.logical_and(idx, celltypes != "line")

        if mesh.dim == 3:
            idx = np.logical_and(idx, celltypes != "quad")
            idx = np.logical_and(idx, celltypes != "triangle")

        if idx.sum() < len(mesh.cells):
            mesh.cells = [cell for keep, cell in zip(idx, mesh.cells) if keep]
            for k, v in cell_data.items():
                mesh.cell_data[k] = np.concatenate(
                    [vv for keep, vv in zip(idx, v) if keep]
                )

            mesh.prune_duplicates()

    return mesh


def write(filename, mesh, file_format=None, **kwargs):
    """
    Write unstructured mesh to file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    mesh : toughio.Mesh
        Mesh to export.
    file_format : str or None, optional, default None
        Output file format.

    Other Parameters
    ----------------
    nodal_distance : str ('line' or 'orthogonal'), optional, default 'line'
        Only if ``file_format = "tough"``. Method to calculate connection nodal distances:
        - 'line': distance between node and common face along connecting line (distance is not normal),
        - 'orthogonal' : distance between node and its orthogonal projection onto common face (shortest distance).
    material_name : dict or None, default None
        Only if ``file_format = "tough"``. Rename cell material.
    material_end : str, array_like or None, default None
        Only if ``file_format = "tough"``. Move cells to bottom of block 'ELEME' if their materials is in `material_end`.
    incon : bool, optional, default False
        Only if ``file_format = "tough"``. If `True`, initial conditions will be written in file `INCON`.
    eos : str or None, optional, default None
        Only if ``file_format = "tough"``. Equation of State.
    gravity : array_like or None, optional, default None
        Only if ``file_format = "tough"``. Gravity direction vector.
    protocol : integer, optional, default `pickle.HIGHEST_PROTOCOL`
        Only if ``file_format = "pickle"``. :mod:`pickle` protocol version.

    """
    # Check file format
    fmt = (
        file_format
        if file_format
        else filetype_from_filename(filename, _extension_to_filetype)
    )

    # Call custom writer
    if fmt in _writer_map:
        if fmt not in {"tough", "pickle"}:
            mesh = deepcopy(mesh)
            mesh.cell_data = {k: mesh.split(v) for k, v in mesh.cell_data.items()}
        _writer_map[fmt](filename, mesh, **kwargs)
    else:
        mesh = mesh.to_meshio()
        meshio.write(filename, mesh, file_format=file_format, **kwargs)


def read_time_series(filename):
    """
    Read time series from XDMF file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name.

    Returns
    -------
    list of namedtuple (type, data)
        Grid cell data.
    list of dict
        Data associated to grid points for each time step.
    list of dict
        Data associated to grid cells for each time step.
    array_like
        Time step values.

    """
    point_data, cell_data, time_steps = [], [], []
    with meshio.xdmf.TimeSeriesReader(filename) as reader:
        points, cells = reader.read_points_cells()

        for k in range(reader.num_steps):
            t, pdata, cdata = reader.read_data(k)
            point_data.append(pdata)
            cell_data.append(cdata)
            time_steps.append(t)

    # Concatenate cell data arrays
    for cdata in cell_data:
        for k in cdata:
            cdata[k] = np.concatenate(cdata[k])

    return points, cells, point_data, cell_data, time_steps


def write_time_series(
    filename,
    points,
    cells,
    point_data=None,
    cell_data=None,
    time_steps=None,
):
    """
    Write time series given points and cells data.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name.
    points : ndarray
        Grid points array.
    cells : list of namedtuple (type, data)
        Grid cell data.
    point_data : list of dict or None, optional, default None
        Data associated to grid points for each time step.
    cell_data : list of dict or None, optional, default None
        Data associated to grid cells for each time step.
    time_steps : array_like, optional, default None
        Time step values.

    """
    import shutil

    filename = pathlib.Path(filename)

    if point_data is not None and not isinstance(point_data, (list, tuple)):
        raise TypeError()
    if cell_data is not None and not isinstance(cell_data, (list, tuple)):
        raise TypeError()
    if time_steps is not None and not isinstance(time_steps, (list, tuple, np.ndarray)):
        raise TypeError()

    if not (point_data or cell_data):
        raise ValueError("Provide at least point_data or cell_data.")
    else:
        nt = len(point_data) if point_data else len(cell_data)

    if point_data and len(point_data) != nt:
        raise ValueError("Inconsistent number of point data.")
    if cell_data and len(cell_data) != nt:
        raise ValueError("Inconsistent number of cell data.")
    if time_steps is not None and len(time_steps) != nt:
        raise ValueError("Inconsistent number of time steps.")

    point_data = point_data if point_data else [{}] * nt
    cell_data = cell_data if cell_data else [{}] * nt
    time_steps = time_steps if time_steps is not None else list(range(nt))

    # Split cell data arrays
    sizes = np.cumsum([len(c.data) for c in cells[:-1]])
    cell_data = [
        {k: np.split(v, sizes) for k, v in cdata.items()} for cdata in cell_data
    ]

    # Sort data with time steps
    idx = np.argsort(time_steps)
    point_data = [point_data[i] for i in idx]
    cell_data = [cell_data[i] for i in idx]
    time_steps = [time_steps[i] for i in idx]

    # Write XDMF
    def write_data(writer, points, cells, point_data, cell_data, time_steps):
        writer.write_points_cells(points, cells)
        for tstep, pdata, cdata in zip(time_steps, point_data, cell_data):
            writer.write_data(tstep, point_data=pdata, cell_data=cdata)

    with meshio.xdmf.TimeSeriesWriter(filename) as writer:
        write_data(writer, points, cells, point_data, cell_data, time_steps)

    # Bug in meshio v5: H5 file is written in the current working directory
    if str(filename.parent) != ".":
        h5_filename = f"{filename.stem}.h5"
        shutil.move(h5_filename, str(filename.parent))
