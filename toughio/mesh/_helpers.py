import meshio
import numpy

from . import avsucd, flac3d, pickle, tecplot, tough
from ._mesh import Mesh, from_meshio

__all__ = [
    "read",
    "write",
    "write_points_cells",
    "read_time_series",
    "write_time_series",
]


_extension_to_filetype = {
    ".dat": "tecplot",
    ".f3grid": "flac3d",
    ".pickle": "pickle",
}


def _filetype_from_filename(filename):
    """Determine file type from its extension."""
    import os

    ext = os.path.splitext(filename)[1].lower()
    return _extension_to_filetype[ext] if ext in _extension_to_filetype.keys() else ""


def read(filename, file_format=None, **kwargs):
    """
    Read unstructured mesh from file.

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
    if not isinstance(filename, str):
        raise TypeError()
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
        mesh = interface.read(filename, *args, **_kwargs)
    else:
        mesh = meshio.read(filename, file_format)
    return mesh if fmt in {"tough", "pickle"} else from_meshio(mesh)


def write(filename, mesh, file_format=None, **kwargs):
    """
    Write unstructured mesh to file.

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
    incon : bool, optional, default False
        Only if ``file_format = "tough"``. If `True`, initial conditions will be written in file `INCON`.

    """
    # Check file format
    if not isinstance(filename, str):
        raise TypeError()
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
                "incon": False,
            },
        ),
        "avsucd": (avsucd, (), {}),
        "flac3d": (flac3d, (), {}),
        "pickle": (pickle, (), {}),
        "tecplot": (tecplot, (), {}),
    }
    mesh = mesh if fmt in {"tough", "pickle"} else mesh.to_meshio()
    if fmt in format_to_writer.keys():
        interface, args, default_kwargs = format_to_writer[fmt]
        _kwargs = default_kwargs.copy()
        _kwargs.update(kwargs)
        interface.write(filename, mesh, *args, **_kwargs)
    else:
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


def read_time_series(filename):
    """
    Read time series from XDMF file.

    Parameters
    ----------
    filename : str
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
    from ._common import get_meshio_version, get_new_meshio_cells

    if not isinstance(filename, str):
        raise ValueError()

    point_data, cell_data, time_steps = [], [], []
    if get_meshio_version() < (3,):
        reader = meshio.XdmfTimeSeriesReader(filename)
        points, cells = reader.read_points_cells()

        for k in range(reader.num_steps):
            t, pdata, cdata = reader.read_data(k)

            _, cdata = get_new_meshio_cells(cells, cdata)
            point_data.append(pdata)
            cell_data.append(cdata)
            time_steps.append(t)

        cells = get_new_meshio_cells(cells)
    else:
        with meshio.xdmf.TimeSeriesReader(filename) as reader:
            points, cells = reader.read_points_cells()

            for k in range(reader.num_steps):
                t, pdata, cdata = reader.read_data(k)
                point_data.append(pdata)
                cell_data.append(cdata)
                time_steps.append(t)

    # Concatenate cell data arrays
    for cdata in cell_data:
        for k in cdata.keys():
            cdata[k] = numpy.concatenate(cdata[k])

    return points, cells, point_data, cell_data, time_steps


def write_time_series(
    filename, points, cells, point_data=None, cell_data=None, time_steps=None,
):
    """
    Write time series given points and cells data.

    Parameters
    ----------
    filename : str
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
    from ._common import get_meshio_version, get_old_meshio_cells

    if not isinstance(filename, str):
        raise TypeError()
    if point_data is not None and not isinstance(point_data, (list, tuple)):
        raise TypeError()
    if cell_data is not None and not isinstance(cell_data, (list, tuple)):
        raise TypeError()
    if time_steps is not None and not isinstance(
        time_steps, (list, tuple, numpy.ndarray)
    ):
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
    sizes = numpy.cumsum([len(c.data) for c in cells[:-1]])
    cell_data = [
        {k: numpy.split(v, sizes) for k, v in cdata.items()} for cdata in cell_data
    ]

    # Sort data with time steps
    idx = numpy.argsort(time_steps)
    point_data = [point_data[i] for i in idx]
    cell_data = [cell_data[i] for i in idx]
    time_steps = [time_steps[i] for i in idx]

    # Write XDMF
    def write_data(writer, points, cells, point_data, cell_data, time_steps):
        writer.write_points_cells(points, cells)
        for tstep, pdata, cdata in zip(time_steps, point_data, cell_data):
            writer.write_data(tstep, point_data=pdata, cell_data=cdata)

    if get_meshio_version() < (3,):
        writer = meshio.XdmfTimeSeriesWriter(filename)
        tmp = [get_old_meshio_cells(cells, cdata) for cdata in cell_data]
        cells = tmp[0][0]
        cell_data = [cell[1] for cell in tmp]
        write_data(writer, points, cells, point_data, cell_data, time_steps)
    else:
        with meshio.xdmf.TimeSeriesWriter(filename) as writer:
            write_data(writer, points, cells, point_data, cell_data, time_steps)
