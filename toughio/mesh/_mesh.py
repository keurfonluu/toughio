import collections
from copy import deepcopy

import meshio
import numpy

from ._common import (
    get_meshio_version,
    get_new_meshio_cells,
    get_old_meshio_cells,
    meshio_data,
)
from ._properties import (
    _connections,
    _face_areas,
    _face_normals,
    _faces,
    _materials,
    _qualities,
    _volumes,
)

__all__ = [
    "Cells",
    "Mesh",
    "from_meshio",
]


Cells = collections.namedtuple("Cells", ["type", "data"])


class Mesh(object):
    def __init__(
        self,
        points,
        cells,
        point_data=None,
        cell_data=None,
        field_data=None,
        point_sets=None,
        cell_sets=None,
    ):
        """
        Unstructured toughio mesh.

        This class is updated following the latest :module:`meshio` version and
        brings backward compatibility with its previous versions.

        Parameters
        ----------
        points : array_like (n_points, 3)
            Cooordinates of points.
        cells : list of tuples (cell_type, data)
            Connectivity of cells.
        point_data : dict or None, optional, default None
            Point data arrays.
        cell_data : dict or None, optional, default None
            Cell data arrays.
        field_data : dict or None, optional, default None
            Field data names.
        point_sets : dict or None, optional, default None
            Sets of points.
        cell_sets : dict or None, optional, default None
            Sets of cells.

        """
        self.points = points
        self.cells = cells
        self.point_data = point_data if point_data else {}
        self.cell_data = cell_data if cell_data else {}
        self.field_data = field_data if field_data else {}
        self.point_sets = point_sets if point_sets else {}
        self.cell_sets = cell_sets if cell_sets else {}

    def __repr__(self):
        """Represent a :class:`toughio.Mesh`."""
        lines = [
            "<toughio mesh object>",
            "  Number of points: {}".format(len(self.points)),
        ]
        if len(self.cells) > 0:
            lines.append("  Number of cells:")
            for tpe, elems in self.cells:
                lines.append("    {}: {}".format(tpe, len(elems)))
        else:
            lines.append("  No cells.")

        if self.point_sets:
            lines.append("  Point sets: {}".format(", ".join(self.point_sets.keys())))

        if self.point_data:
            lines.append("  Point data: {}".format(", ".join(self.point_data.keys())))

        if self.cell_data:
            lines.append("  Cell data: {}".format(", ".join(self.cell_data.keys())))

        return "\n".join(lines)

    def extrude_to_3d(self, height=1.0, axis=2, inplace=True):
        """
        Convert a 2D mesh to 3D by extruding cells along given axis.

        Parameters
        ----------
        height : scalar or array_like, optional, default 1.0
            Height of extrusion.
        axis : int (0, 1 or 2), optional, default 2
            Axis along which extrusion is performed.
        inplace : bool, optional, default True
            If `False`, return a new :class:`toughio.Mesh`.

        Returns
        -------
        toughio.Mesh
            Extruded mesh (only if ``inplace == False``).

        """
        if axis not in [0, 1, 2]:
            raise ValueError("axis must be 0, 1 or 2.")
        mesh = self if inplace else deepcopy(self)
        height = [height] if isinstance(height, (int, float)) else height

        npts, nh = len(mesh.points), len(height)
        if mesh.points.shape[1] == 3:
            if len(set(mesh.points[:, axis])) != 1:
                raise ValueError("Cannot extrude mesh along axis {}.".format(axis))
        else:
            mesh.points = numpy.column_stack((mesh.points, numpy.zeros(npts)))
            if axis != 2:
                mesh.points[:, [axis, 2]] = mesh.points[:, [2, axis]]

        extra_points = numpy.array(mesh.points)
        for h in height:
            extra_points[:, axis] += h
            mesh.points = numpy.vstack((mesh.points, extra_points))
        for k, v in mesh.point_data.items():
            mesh.point_data[k] = numpy.tile(v, nh + 1)

        extruded_types = {
            "triangle": "wedge",
            "quad": "hexahedron",
        }
        cells = []
        cell_data = {k: mesh.split(v) for k, v in mesh.cell_data.items()}
        for ic, c in enumerate(mesh.cells):
            if c.type in extruded_types.keys():
                extruded_type = extruded_types[c.type]
                nr, nc = c.data.shape
                cell = Cells(extruded_type, numpy.tile(c.data, (nh, 2)))
                for i in range(nh):
                    ibeg, iend = i * nr, (i + 1) * nr
                    cell.data[ibeg:iend, :nc] += i * npts
                    cell.data[ibeg:iend, nc:] += (i + 1) * npts
                cells.append(cell)

                for k, v in cell_data.items():
                    v[ic] = numpy.tile(v[ic], nh)
        mesh.cells = cells
        mesh.cell_data = {k: numpy.concatenate(v) for k, v in cell_data.items()}

        if mesh.field_data:
            for k in mesh.field_data.keys():
                mesh.field_data[k][1] = 3

        if not inplace:
            return mesh

    def prune_duplicates(self, inplace=True):
        """
        Delete duplicate points and cells.

        Parameters
        ----------
        inplace : bool, optional, default True
            If `False`, return a new :class:`toughio.Mesh`.

        Returns
        -------
        toughio.Mesh
            Pruned mesh (only if ``inplace == False``).

        Note
        ----
        Does not preserve points order from original array in mesh.

        """
        mesh = self if inplace else deepcopy(self)
        cells = [[c.type, c.data] for c in mesh.cells]

        # Prune duplicate points
        unique_points, pind, pinv = numpy.unique(
            mesh.points, axis=0, return_index=True, return_inverse=True,
        )
        if len(unique_points) < len(mesh.points):
            mesh.points = unique_points
            for k, v in mesh.point_data.items():
                mesh.point_data[k] = v[pind]
            for ic, (k, v) in enumerate(cells):
                cells[ic][1] = pinv[v]

        # Prune duplicate cells
        cell_data = {k: mesh.split(v) for k, v in mesh.cell_data.items()}
        for ic, (k, v) in enumerate(cells):
            vsort = numpy.sort(v, axis=1)
            _, order = numpy.unique(vsort, axis=0, return_index=True)
            cells[ic][1] = v[order]
            for kk, vv in cell_data.items():
                cell_data[kk][ic] = vv[ic][order]
        mesh.cells = cells
        mesh.cell_data = {k: numpy.concatenate(v) for k, v in cell_data.items()}

        if not inplace:
            return mesh

    def split(self, arr):
        """
        Split input array into subarrays for each cell block in mesh.

        Parameters
        ----------
        arr : array_like
            Input array.

        Returns
        -------
        list of array_like
            List of subarrays.

        """
        if len(arr) != self.n_cells:
            raise ValueError()
        sizes = numpy.cumsum([len(c.data) for c in self.cells])

        return numpy.split(numpy.asarray(arr), sizes[:-1])

    def to_meshio(self):
        """
        Convert mesh to :class:`meshio.Mesh`.

        Returns
        -------
        meshio.Mesh
            Output mesh.

        """
        keys = ["points", "point_data", "field_data"]
        kwargs = {key: getattr(self, key) for key in keys}

        version = get_meshio_version()
        cell_data = {k: self.split(v) for k, v in self.cell_data.items()}
        if version[0] >= 4:
            kwargs.update(
                {
                    "cells": self.cells,
                    "cell_data": cell_data,
                    "point_sets": self.point_sets,
                    "cell_sets": self.cell_sets,
                }
            )
        else:
            cells, cell_data = get_old_meshio_cells(self.cells, cell_data)
            kwargs.update(
                {"cells": cells, "cell_data": cell_data, "node_sets": self.point_sets,}
            )

        return meshio.Mesh(**kwargs)

    def to_pyvista(self):
        """
        Convert mesh to :class:`pyvista.UnstructuredGrid`.

        Returns
        -------
        pyvista.UnstructuredGrid
            Output mesh.

        """
        try:
            import pyvista
            from ._common import (
                meshio_to_vtk_type,
                vtk_type_to_numnodes,
            )
        except ImportError:
            raise ImportError(
                "Converting to pyvista.UnstructuredGrid requires pyvista to be installed."
            )

        # Extract cells from toughio.Mesh object
        offset = []
        cells = []
        cell_type = []
        next_offset = 0
        for c in self.cells:
            vtk_type = meshio_to_vtk_type[c.type]
            numnodes = vtk_type_to_numnodes[vtk_type]
            offset += [next_offset + i * (numnodes + 1) for i in range(len(c.data))]
            cells.append(
                numpy.hstack((numpy.full((len(c.data), 1), numnodes), c.data)).ravel()
            )
            cell_type += [vtk_type] * len(c.data)
            next_offset = offset[-1] + numnodes + 1

        # Create pyvista.UnstructuredGrid object
        points = self.points
        if points.shape[1] == 2:
            points = numpy.hstack((points, numpy.zeros((len(points), 1))))

        mesh = pyvista.UnstructuredGrid(
            numpy.array(offset),
            numpy.concatenate(cells),
            numpy.array(cell_type),
            numpy.array(points, numpy.float64),
        )

        # Set point data
        mesh.point_arrays.update(
            {k: numpy.array(v, numpy.float64) for k, v in self.point_data.items()}
        )

        # Set cell data
        mesh.cell_arrays.update(self.cell_data)

        return mesh

    def to_tough(self, filename="MESH", **kwargs):
        """
        Write TOUGH `MESH` file.

        Parameters
        ----------
        filename : str, optional, default 'MESH'
            Output file name.

        Other Parameters
        ----------------
        nodal_distance : str ('line' or 'orthogonal'), optional, default 'line'
            Method to calculate connection nodal distances:
            - 'line': distance between node and common face along connecting
            line (distance is not normal),
            - 'orthogonal' : distance between node and its orthogonal
            projection onto common face (shortest distance).
        material_name : dict or None, default None
            Rename cell material.
        material_end : str, array_like or None, default None
            Move cells to bottom of block 'ELEME' if their materials is in `material_end`.
        incon : bool, optional, default False
            If `True`, initial conditions will be written in file `INCON`.

        """
        self.write(filename, file_format="tough", **kwargs)

    def read_output(self, file_or_output, time_step=-1):
        """
        Import TOUGH results to the mesh.

        Parameters
        ----------
        file_or_output : str, namedtuple or list of namedtuple
            Input file name or output data.
        time_step : int, optional, default -1
            Data for given time step to import. Default is last time step.

        """
        from .. import read_output
        from .._io._helpers import Output, Save, _reorder_labels

        if not isinstance(file_or_output, (str, list, tuple, Output, Save)):
            raise TypeError()
        if not isinstance(time_step, int):
            raise TypeError()

        if isinstance(file_or_output, str):
            out = read_output(file_or_output)
        else:
            out = file_or_output

        if not isinstance(out, (Output, Save)):
            if not (-len(out) <= time_step < len(out)):
                raise ValueError()
            out = out[time_step]

        if len(out.labels) != self.n_cells:
            raise ValueError()
        out = _reorder_labels(out, self.labels)
        self.cell_data.update(out.data)

    def write(self, filename, file_format=None, **kwargs):
        """
        Write mesh to file.

        Parameters
        ----------
        filename : str
            Output file name.
        file_format : str or None, optional, default None
            Output file format. If `None`, it will be guessed from file's
            extension. To write TOUGH MESH, `file_format` must be specified
            as 'tough' (no specific extension exists for TOUGH MESH).

        """
        from ._helpers import write

        write(filename, self, file_format, **kwargs)

    def plot(self, *args, **kwargs):
        """Display mesh using :method:`pyvista.UnstructuredGrid.plot``."""
        mesh = self.to_pyvista()
        mesh.plot(*args, **kwargs)

    def add_point_data(self, label, data):
        """
        Add a new point data array.

        Parameters
        ----------
        label : str
            Point data array name.
        data : array_like
            Point data array.

        """
        if not isinstance(label, str):
            raise TypeError()
        if not isinstance(data, (list, tuple, numpy.ndarray)):
            raise TypeError()
        if len(data) != self.n_points:
            raise ValueError()
        self.point_data[label] = numpy.asarray(data)

    def add_cell_data(self, label, data):
        """
        Add a new cell data array.

        Parameters
        ----------
        label : str
            Cell data array name.
        data : array_like
            Cell data array.

        """
        if not isinstance(label, str):
            raise TypeError()
        if not isinstance(data, (list, tuple, numpy.ndarray)):
            raise TypeError()
        if len(data) != self.n_cells:
            raise ValueError()
        self.cell_data[label] = numpy.asarray(data)

    def set_material(self, material, xlim=None, ylim=None, zlim=None):
        """
        Set material to cells in box.

        Set material for cells within box selection defined by `xlim`, `ylim` and `zlim`.

        Parameters
        ----------
        material : str
            Material name.
        xlim : array_like or None, optional, default None
            Minimum and maximum values in X direction.
        ylim : array_like or None, optional, default None
            Minimum and maximum values in Y direction.
        zlim : array_like or None, optional, default None
            Minimum and maximum values in Z direction.

        Raises
        ------
        AssertionError
            If any input argument is not valid.

        """

        def isinbounds(x, bounds):
            return (
                numpy.logical_and(x >= min(bounds), x <= max(bounds))
                if bounds is not None
                else numpy.ones(len(x), dtype=bool)
            )

        if not isinstance(material, str):
            raise TypeError()
        if not (xlim is not None or ylim is not None or zlim is not None):
            raise TypeError()
        if not (
            xlim is None
            or (isinstance(xlim, (list, tuple, numpy.ndarray)) and len(xlim) == 2)
        ):
            raise ValueError()
        if not (
            ylim is None
            or (isinstance(ylim, (list, tuple, numpy.ndarray)) and len(ylim) == 2)
        ):
            raise ValueError()
        if not (
            zlim is None
            or (isinstance(zlim, (list, tuple, numpy.ndarray)) and len(zlim) == 2)
        ):
            raise ValueError()

        x, y, z = self.centers.T
        mask_x = isinbounds(x, xlim)
        mask_y = isinbounds(y, ylim)
        mask_z = isinbounds(z, zlim)
        mask = numpy.logical_and(numpy.logical_and(mask_x, mask_y), mask_z)

        if mask.any():
            data = self.cell_data["material"]
            imat = (
                self.field_data[material][0]
                if material in self.field_data.keys()
                else data.max() + 1
            )
            data[mask] = imat
            self.add_cell_data("material", data)
            self.field_data[material] = numpy.array([imat, 3])

    def near(self, point):
        """
        Return local index of cell nearest to query point.

        Parameters
        ----------
        point : array_like
            Coordinates of point to query.

        Returns
        -------
        tuple
            Local index of cell as a tuple (iblock, icell).

        """
        if not isinstance(point, (list, tuple, numpy.ndarray)):
            raise TypeError()
        if numpy.ndim(point) != 1:
            raise ValueError()
        if len(point) != self.points.shape[1]:
            raise ValueError()

        idx = numpy.arange(self.n_cells)
        idx = idx[numpy.argmin(numpy.linalg.norm(self.centers - point, axis=1))]

        return idx

    @property
    def points(self):
        """Return coordinates of points."""
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def cells(self):
        """Return connectivity of cells."""
        if self._cells:
            return self._cells
        else:
            return [Cells(k, v) for k, v in self._cells_dict.items()]

    @cells.setter
    def cells(self, value):
        if isinstance(value, dict):
            self._cells = []
            self._cells_dict = value
        else:
            self._cells = [Cells(k, v) for k, v in value]
            self._cells_dict = {}

    @property
    def cells_dict(self):
        """Return connectivity of cells (``meshio < 4.0.0``)."""
        if self._cells:
            return get_old_meshio_cells(self._cells)
        else:
            return self._cells_dict

    @property
    def point_data(self):
        """Return point data arrays."""
        return self._point_data

    @point_data.setter
    def point_data(self, value):
        self._point_data = value

    @property
    def cell_data(self):
        """Return cell data arrays."""
        return self._cell_data

    @cell_data.setter
    def cell_data(self, value):
        self._cell_data = value

    @property
    def field_data(self):
        """Return field data names."""
        return self._field_data

    @field_data.setter
    def field_data(self, value):
        self._field_data = value

    @property
    def point_sets(self):
        """Return sets of points."""
        return self._point_sets

    @point_sets.setter
    def point_sets(self, value):
        self._point_sets = value

    @property
    def cell_sets(self):
        """Return sets of cells."""
        return self._cell_sets

    @cell_sets.setter
    def cell_sets(self, value):
        self._cell_sets = value

    @property
    def n_points(self):
        """Return number of points."""
        return len(self.points)

    @property
    def n_cells(self):
        """Return number of cells."""
        return sum(len(c.data) for c in self.cells)

    @property
    def labels(self):
        """Return labels of cell in mesh."""
        from ._common import labeler

        return numpy.array([labeler(i) for i in range(self.n_cells)])

    @property
    def centers(self):
        """Return node centers of cell in mesh."""
        return numpy.concatenate([self.points[c.data].mean(axis=1) for c in self.cells])

    @property
    def materials(self):
        """Return materials of cell in mesh."""
        return _materials(self)

    @property
    def faces(self):
        """Return connectivity of faces of cell in mesh."""
        out = _faces(self)
        arr = numpy.full((self.n_cells, 6, 4), -1)
        for i, x in enumerate(out):
            arr[i, : len(x[0]), : x[0].shape[1]] = x[0]
            if len(x) > 1:
                arr[i, len(x[0]) : len(x[0]) + len(x[1]), : x[1].shape[1]] = x[1]
        return arr

    @property
    def face_normals(self):
        """Return normal vectors of faces in mesh."""
        return _face_normals(self)

    @property
    def face_areas(self):
        """Return areas of faces in mesh."""
        return _face_areas(self)

    @property
    def volumes(self):
        """Return volumes of cell in mesh."""
        return _volumes(self)

    @property
    def connections(self):
        """
        Return mesh connections.

        Assume conformity and that points and cells are uniquely defined in mesh.

        Note
        ----
        Only for 3D meshes and first order cells.

        """
        return _connections(self)

    @property
    def qualities(self):
        """
        Return qualities of cells in mesh.

        The quality of a cell is measured as the average cosine angle between the
        connection line and the interface normal vectors.

        """
        return numpy.array([numpy.mean(out) for out in _qualities(self)])


def from_meshio(mesh):
    """
    Convert a :class:`meshio.Mesh` to :class:`toughio.Mesh`.

    Parameters
    ----------
    mesh : meshio.Mesh
        Input mesh.

    Returns
    -------
    toughio.Mesh
        Output mesh.

    """
    if mesh.cell_data:
        version = get_meshio_version()
        if version[0] >= 4:
            cells = mesh.cells
            cell_data = mesh.cell_data
        else:
            cells, cell_data = get_new_meshio_cells(mesh.cells, mesh.cell_data)

        for k in cell_data.keys():
            if k in meshio_data:
                cell_data["material"] = cell_data.pop(k)
                break

        cell_data = {k: numpy.concatenate(v) for k, v in cell_data.items()}
    else:
        cell_data = {}

    out = Mesh(
        points=mesh.points,
        cells=cells,
        point_data=mesh.point_data,
        cell_data=cell_data,
        field_data=mesh.field_data,
        point_sets=(
            mesh.point_sets
            if hasattr(mesh, "point_sets")
            else mesh.node_sets
            if hasattr(mesh, "node_sets")
            else None
        ),
        cell_sets=mesh.cell_sets if hasattr(mesh, "cell_sets") else None,
    )

    if "material" not in out.cell_data.keys():
        imat = (
            numpy.max([v[0] for v in mesh.field_data.values() if v[1] == 3]) + 1
            if mesh.field_data
            else 1
        )
        out.cell_data["material"] = numpy.full(out.n_cells, imat, dtype=int)
        out.field_data["dfalt"] = numpy.array([imat, 3])

    return out
