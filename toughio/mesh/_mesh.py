import collections
import logging
import numpy
import meshio
from copy import deepcopy

from ._common import get_meshio_version

__all__ = [
    "Cells",
    "Mesh",
    "_meshio_to_toughio_mesh",
]


Cells = collections.namedtuple("Cells", ["type", "data"])


class Mesh(meshio.Mesh):

    def __init__(
        self,
        points,
        cells,
        point_data = None,
        cell_data = None,
        field_data = None,
        point_sets = None,
        cell_sets = None,
        gmsh_periodic = None,
        info = None,
        ):
        self.points = points
        self.cells = cells
        self.point_data = point_data if point_data else {}
        self.cell_data = cell_data if cell_data else {}
        self.field_data = field_data if field_data else {}
        self.point_sets = point_sets if point_sets else {}
        self.cell_sets = cell_sets if cell_sets else {}
        self.gmsh_periodic = gmsh_periodic
        self.info = info

    def __repr__(self):
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

    def itercells(self):
        """
        Iterate over cells as namedtuples.

        Returns
        -------
        generator
            An object to iterate over namedtuples for each cell in the mesh.
        """
        for cell in self.cells:
            for c in cell.data:
                yield Cells(cell.type, c)

    def extrude_to_3d(self, height = 1., axis = 2, inplace = True):
        """
        Convert a 2D mesh to 3D by extruding cells along given axis.

        Parameters
        ----------
        height : scalar or array_like, optional, default 1.
            Height of extrusion.
        axis : int (0, 1 or 2), optional, default 2
            Axis along which extrusion is performed.
        inplace : bool, optional, default True
            If `True`, overwrite input Mesh object. Otherwise, return a new
            Mesh.

        Returns
        -------
        toughio.Mesh
            Extruded mesh (only if ``inplace == False``).
        """
        assert axis in [ 0, 1, 2 ], "axis must be 0, 1 or 2."
        mesh = self if inplace else deepcopy(self)
        height = [ height ] if isinstance(height, (int, float)) else height

        npts, nh = len(mesh.points), len(height)
        if mesh.points.shape[1] == 3:
            assert len(set(mesh.points[:,axis])) == 1, (
                "Cannot extrude mesh along axis {}.".format(axis)
            )
        else:
            mesh.points = numpy.column_stack((mesh.points, numpy.zeros(npts)))
            if axis != 2:
                mesh.points[:,[axis,2]] = mesh.points[:,[2,axis]]

        extra_points = numpy.array(mesh.points)
        for h in height:
            extra_points[:,axis] += h
            mesh.points = numpy.vstack((mesh.points, extra_points))

        extruded_types = {
            "triangle": "wedge",
            "quad": "hexahedron",
        }
        cells = []
        for ic, c in enumerate(mesh.cells):
            if c.type in extruded_types.keys():
                extruded_type = extruded_types[c.type]
                nr, nc = c.data.shape
                cell = Cells(extruded_type, numpy.tile(c.data, (nh, 2)))
                for i in range(nh):
                    ibeg, iend = i*nr, (i+1)*nr
                    cell.data[ibeg:iend,:nc] += i*npts
                    cell.data[ibeg:iend,nc:] += (i+1)*npts
                cells.append(cell)

                if mesh.cell_data:
                    for k, v in mesh.cell_data.items():
                        v[ic] = numpy.tile(v[ic], nh)
        mesh.cells = cells

        if mesh.field_data:
            for k in mesh.field_data.keys():
                mesh.field_data[k][1] = 3

        if not inplace:
            return mesh

    def prune_duplicates(self, inplace = True):
        """
        Delete duplicate points and cells.

        Parameters
        ----------
        inplace : bool, optional, default True
            If `True`, overwrite input Mesh object. Otherwise, return a new
            Mesh.

        Returns
        -------
        toughio.Mesh
            Pruned mesh (only if ``inplace == False``).
        
        Note
        ----
        Does not preserve points order from original array in mesh.
        """
        mesh = self if inplace else deepcopy(self)
        cells = mesh.cells_dict

        # Prune duplicate points
        unique_points, pind, pinv = numpy.unique(
            mesh.points,
            axis = 0,
            return_index = True,
            return_inverse = True,
        )
        if len(unique_points) < len(mesh.points):
            mesh.points = unique_points
            for k, v in mesh.point_data.items():
                mesh.point_data[k] = v[pind]
            for k, v in cells.items():
                cells[k] = pinv[v]

        # Prune duplicate cells
        for ic, (k, v) in enumerate(cells.items()):
            vsort = numpy.sort(v, axis = 1)
            _, order = numpy.unique(vsort, axis = 0, return_index = True)
            cells[k] = cells[k][order]
            if mesh.cell_data:
                for kk, vv in mesh.cell_data.items():
                    mesh.cell_data[kk][ic] = vv[ic][order]
        mesh.cells = cells

        if not inplace:
            return mesh

    def rename_cell_data(self, key):
        """
        Rename cell_data keywords.

        Parameters
        ----------
        key : dict
            Keywords to rename in the form ``{old: new}`` where ``old`` and
            ``new`` are both strings.
        """
        for old, new in key.items():
            if old in self.cell_data.keys():
                self.cell_data[new] = self._cell_data.pop(old)

    def to_meshio(self):
        """
        Convert mesh to meshio.Mesh.

        Returns
        -------
        meshio.Mesh
            Output mesh.
        """
        keys = ["points", "point_data", "field_data", "gmsh_periodic"]
        kwargs = {key: getattr(self, key) for key in keys}

        version = get_meshio_version()
        if version[0] >= 4:
            kwargs.update({
                "cells": self.cells,
                "cell_data": self.cell_data,
                "point_sets": self.point_sets,
                "cell_sets": self.cell_sets,
            })
        else:
            cell_data = {}
            if self.cell_data:
                for ic, c in enumerate(self.cells):
                    if c.type not in cell_data.keys():
                        cell_data[c.type] = {}
                    for k, v in self.cell_data.items():
                        cell_data[c.type][k] = v[ic]
            kwargs.update({
                "cells": self.cells_dict,
                "cell_data": cell_data,
                "node_sets": self.point_sets,
            })
        if version[0] >= 3:
            kwargs["info"] = self.info

        return meshio.Mesh(**kwargs)

    def to_pyvista(self):
        """
        Convert mesh to pyvista.UnstructuredGrid.

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
            raise ModuleNotFoundError(
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
            offset += [next_offset+i*(numnodes+1) for i in range(len(c.data))]
            cells.append(numpy.hstack((numpy.full((len(c.data), 1), numnodes), c.data)).ravel())
            cell_type += [vtk_type] * len(c.data)
            next_offset = offset[-1] + numnodes + 1

        # Extract cell data from toughio.Mesh object
        cell_data = {k: numpy.concatenate(v) for k, v in self.cell_data.items()}

        # Create pyvista.UnstructuredGrid object
        points = self.points
        if points.shape[1] == 2:
            points = numpy.hstack((points, numpy.zeros((len(points),1))))

        mesh = pyvista.UnstructuredGrid(
            numpy.array(offset),
            numpy.concatenate(cells),
            numpy.array(cell_type),
            numpy.array(points, numpy.float64),
        )

        # Set point data
        mesh.point_arrays.update({k: numpy.array(v, numpy.float64) for k, v in self.point_data.items()})

        # Set cell data
        mesh.cell_arrays.update(cell_data)

        return mesh

    def plot(self, *args, **kwargs):
        """
        Display mesh using method ``pyvista.UnstructuredGrid.plot``.
        """
        mesh = self.to_pyvista()
        mesh.plot(*args, **kwargs)

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def cells(self):
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
            self._cells = value
            self._cells_dict = {}

    @property
    def cells_dict(self):
        if self._cells:
            assert len(self._cells) == len(
                numpy.unique([c.type for c in self._cells])
            ), "More than one block of the same type. Cannot create dictionary."
            return dict(self._cells)
        else:
            return self._cells_dict

    @property
    def point_data(self):
        return self._point_data

    @point_data.setter
    def point_data(self, value):
        self._point_data = value

    @property
    def cell_data(self):
        return self._cell_data

    @cell_data.setter
    def cell_data(self, value):
        self._cell_data = value

    @property
    def field_data(self):
        return self._field_data

    @field_data.setter
    def field_data(self, value):
        self._field_data = value

    @property
    def point_sets(self):
        return self._point_sets

    @point_sets.setter
    def point_sets(self, value):
        self._point_sets = value

    @property
    def cell_sets(self):
        return self._cell_sets

    @cell_sets.setter
    def cell_sets(self, value):
        self._cell_sets = value

    @property
    def gmsh_periodic(self):
        return self._gmsh_periodic

    @gmsh_periodic.setter
    def gmsh_periodic(self, value):
        self._gmsh_periodic = value

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        self._info = value

    @property
    def n_points(self):
        return len(self.points)

    @property
    def n_cells(self):
        return sum(len(c.data) for c in self.cells)

    @property
    def connectivity(self):
        """
        Returns mesh connectivity assuming conformity and that points and
        cells are uniquely defined in mesh (use ``prune_duplicates`` otherwise).

        Note
        ----
        Only for 3D meshes and first order cells.
        """
        assert numpy.shape(self.points)[1] == 3, (
            "Connectivity for 2D mesh has not been implemented yet."
        )

        # Reconstruct all the faces
        _faces = {
            "tetra": {
                "triangle": [
                    [ 0, 1, 2 ],
                    [ 0, 1, 3 ],
                    [ 1, 2, 3 ],
                    [ 0, 2, 3 ],
                ],
            },
            "pyramid": {
                "triangle": [
                    [ 0, 1, 4 ],
                    [ 1, 2, 4 ],
                    [ 2, 3, 4 ],
                    [ 0, 3, 4 ],
                ],
                "quad": [
                    [ 0, 1, 2, 3 ],
                ],
            },
            "wedge": {
                "triangle": [
                    [ 0, 1, 2 ],
                    [ 3, 4, 5 ],
                ],
                "quad": [
                    [ 0, 1, 3, 4 ],
                    [ 1, 2, 4, 5 ],
                    [ 0, 2, 3, 5 ],
                ],
            },
            "hexahedron": {
                "quad": [
                    [ 0, 1, 2, 3 ],
                    [ 4, 5, 6, 7 ],
                    [ 0, 1, 4, 5 ],
                    [ 1, 2, 5, 6 ],
                    [ 2, 3, 6, 7 ],
                    [ 0, 3, 4, 7 ],
                ],
            },
        }

        faces = { "triangle": [], "quad": [] }
        face_cells = { "triangle": [], "quad": [] }
        for i, cell in enumerate(self.itercells()):
            for mt, mi in _faces[cell.type].items():
                faces[mt] += [cell.data[ii] for ii in mi]
                face_cells[mt] += [i] * len(mi)
        faces = {k: numpy.sort(v, axis = 1) for k, v in faces.items()}

        # Prune duplicate faces
        uf, tmp = {}, {}
        for k, v in faces.items():
            up, uf[k] = numpy.unique(v, axis = 0, return_inverse = True)
            tmp[k] = [[] for _ in range(len(up))]

        # Make connections
        for k, v in uf.items():
            for i, j in enumerate(v):
                tmp[k][j].append(face_cells[k][i])
        conn = [vv for v in tmp.values() for vv in v if len(vv) == 2]

        # Reorganize output
        out = [[] for _ in range(sum(len(c.data) for c in self.cells))]
        for i1, i2 in conn:
            out[i1].append(i2)
            out[i2].append(i1)
        return out


def _meshio_to_toughio_mesh(mesh):
    """
    Convert a meshio.Mesh to toughio.Mesh.
    """
    if mesh.cell_data:
        version = get_meshio_version()
        if version[0] >= 4:
            cell_data = mesh.cell_data
        else:
            labels = numpy.unique([kk for k, v in mesh.cell_data.items() for kk in v.keys()])
            cell_data = {k: [] for k in labels}
            for k in cell_data.keys():
                for kk in mesh.cells.keys():
                    cell_data[k].append(mesh.cell_data[kk][k])
    else:
        cell_data = {}

    return Mesh(
        points = mesh.points,
        cells = mesh.cells,
        point_data = mesh.point_data,
        cell_data = cell_data,
        field_data = mesh.field_data,
        point_sets = (
            mesh.point_sets if hasattr(mesh, "point_sets")
            else mesh.node_sets if hasattr(mesh, "node_sets")
            else None
        ),
        cell_sets = mesh.cell_sets if hasattr(mesh, "cell_sets") else None,
        gmsh_periodic = mesh.gmsh_periodic,
        info = mesh.info if hasattr(mesh, "info") else None,
    )