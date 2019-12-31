# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from __future__ import division, with_statement, unicode_literals

import logging

import numpy as np

from copy import deepcopy
import meshio

__all__ = [
    "extrude_to_3d",
    "build_connectivity",
    "prune_duplicates",
    "rename_cell_data",
    "create_grid",
]


def extrude_to_3d(mesh, height = 1., axis = 2, inplace = False):
    """
    Convert a 2D mesh to 3D by extruding cells along given axis.

    Parameters
    ----------
    mesh : Mesh
        Input mesh to convert.
    height : scalar or array_like, optional, default 1.
        Height of extrusion.
    axis : int (0, 1 or 2), optional, default 2
        Axis along which extrusion is performed.
    inplace : bool, optional, default False
        If `True`, overwrite input Mesh object. Otherwise, return a new
        Mesh.

    Returns
    -------
    Mesh
        Extruded mesh (only if ``inplace == False``).
    """
    assert axis in [ 0, 1, 2 ], "axis must be 0, 1 or 2."
    msh = mesh if inplace else deepcopy(mesh)
    height = [ height ] if isinstance(height, (int, float)) else height

    npts, nh = len(msh.points), len(height)
    if msh.points.shape[1] == 3:
        assert len(set(msh.points[:,axis])) == 1, \
        "Cannot extrude mesh along axis {}.".format(axis)
    else:
        msh.points = np.c_[msh.points,np.zeros(npts)]
        if axis != 2:
            msh.points[:,[axis,2]] = msh.points[:,[2,axis]]

    extra_points = np.array(msh.points)
    for h in height:
        extra_points[:,axis] += h
        msh.points = np.r_[msh.points,extra_points]

    extruded_types = {
        "triangle": "wedge",
        "quad": "hexahedron",
    }
    for k in msh.cells.keys():
        if k in extruded_types.keys():
            extruded_type = extruded_types[k]
            v = msh.cells.pop(k)
            nr, nc = v.shape
            msh.cells[extruded_type] = np.tile(v, (nh, 2))
            for i in range(nh):
                ibeg, iend = i*nr, (i+1)*nr
                msh.cells[extruded_type][ibeg:iend,:nc] += i*npts
                msh.cells[extruded_type][ibeg:iend,nc:] += (i+1)*npts

            if k in msh.cell_data.keys():
                msh.cell_data[extruded_type] = msh.cell_data.pop(k)
                for kk, vv in msh.cell_data[extruded_type].items():
                    msh.cell_data[extruded_type][kk] = np.tile(vv, nh)

    if msh.field_data:
        for k in msh.field_data.keys():
            msh.field_data[k][1] = 3

    if not inplace:
        return msh


def build_connectivity(mesh):
    """
    Build mesh connectivity assuming conformity and that points and cells
    are uniquely defined in mesh (use prune_duplicates otherwise).

    Parameters
    ----------
    mesh : Mesh
        Input mesh.

    Note
    ----
    Only for 3D meshes.
    """
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
    elem_list, count = [], 0
    for k, v in mesh.cells.items():
        for i, vv in enumerate(v):
            for mt, mi in _faces[k].items():
                faces[mt] += [ vv[ii] for ii in mi ]
                face_cells[mt] += [ count for _ in range(len(mi)) ]
            elem_list.append(( k, i ))
            count += 1
    faces = { k: np.sort(v, axis = 1) for k, v in faces.items() }

    # Prune duplicate faces
    uf, tmp = {}, {}
    for k, v in faces.items():
        up, uf[k] = np.unique(v, axis = 0, return_inverse = True)
        tmp[k] = [ [] for _ in range(len(up)) ]

    # Make connections
    for k, v in uf.items():
        for i, j in enumerate(v):
            tmp[k][j].append(face_cells[k][i])
    conn = [ vv for v in tmp.values() for vv in v if len(vv) == 2 ]

    # Reorganize output
    out = {
        k: { i: { kk: [] for kk in mesh.cells.keys() }
        for i in range(len(v)) } for k, v in mesh.cells.items()
    }
    counter = {
        k: { i: { kk: 0 for kk in mesh.cells.keys() }
        for i in range(len(v)) } for k, v in mesh.cells.items()
    }
    for i, j in conn:
        i1, i2 = elem_list[i]
        j1, j2 = elem_list[j]
        out[i1][i2][j1].append(j2)
        out[j1][j2][i1].append(i2)
        counter[i1][i2][j1] += 1
        counter[j1][j2][i1] += 1

    # Sanity check and tidy up
    for k, v in counter.items():
        for kk, vv in v.items():
            for mt, mi in vv.items():
                if not mi:
                    out[k][kk].pop(mt, None)
            if not out[k][kk]:
                logging.warning(
                    "{} {} is not connected to any cell.".format(k, kk)
                )
    return out


def prune_duplicates(mesh, inplace = False):
    """
    Delete duplicate points and cells.

    Parameters
    ----------
    mesh : Mesh
        Input mesh.
    inplace : bool, optional, default False
        If `True`, overwrite input Mesh object. Otherwise, return a new
        Mesh.

    Returns
    -------
    Mesh
        Extruded mesh (only if ``inplace == False``).
    
    Note
    ----
    Does not preserve points order from original array in mesh.
    """
    msh = mesh if inplace else deepcopy(mesh)

    # Prune duplicate points
    unique_points, pinv = np.unique(
        msh.points,
        axis = 0,
        return_inverse = True,
    )
    if len(unique_points) < len(mesh.points):
        msh.points = unique_points
        for k, v in msh.cells.items():
            msh.cells[k] = pinv[v]

    # Prune duplicate cells
    for k, v in msh.cells.items():
        vsort = np.sort(v, axis = 1)
        _, order = np.unique(vsort, axis = 0, return_index = True)
        msh.cells[k] = msh.cells[k][order]
        if msh.cell_data:
            for kk, vv in msh.cell_data[k].items():
                msh.cell_data[k][kk] = vv[order]

    if not inplace:
        return msh


def rename_cell_data(mesh, key):
    """
    Rename cell_data keywords.

    Parameters
    ----------
    mesh : Mesh
        Input mesh to rename.
    key : dict
        Keywords to rename in the form ``{ old: new }`` where ``old`` and
        ``new`` are both strings.
    """
    for v in mesh.cell_data.values():
        for old, new in key.items():
            if old in v.keys():
                v[new] = v.pop(old)


def create_grid(dx, dy, dz = None):
    """
    Generate 2D or 3D irregular cartesian grid.

    Parameters
    ----------
    dx : array_like
        Grid spacing along X axis.
    dy : array_like
        Grid spacing along Y axis.
    dz : array_like or None, optional, default None
        Grid spacing along Z axis. If `None`, generate 2D grid.

    Returns
    -------
    Mesh
        Cartesian mesh.
    """
    points, cells = _grid_3d(dx, dy, dz) if dz else _grid_2d(dx, dy)
    return meshio.Mesh(
        points = points,
        cells = cells,
    )


def _grid_3d(dx, dy, dz):
    """
    Generate 3D cartesian grid.
    """
    # Internal functions
    def meshgrid(x, y, z, indexing = "ij", order = "F"):
        X, Y, Z = np.meshgrid(x, y, z, indexing = indexing)
        return X.ravel(order), Y.ravel(order), Z.ravel(order)

    def mesh_vertices(i, j, k):
        return [
            [ i, j, k ],
            [ i+1, j, k ],
            [ i+1, j+1, k ],
            [ i, j+1, k ],
            [ i, j, k+1 ],
            [ i+1, j, k+1 ],
            [ i+1, j+1, k+1 ],
            [ i, j+1, k+1 ],
        ]

    # Grid
    nx, ny, nz = len(dx), len(dy), len(dz)
    xyz_shape = [ nx+1, ny+1, nz+1 ]
    ijk_shape = [ nx, ny, nz ]
    X, Y, Z = meshgrid(*[ np.cumsum(np.r_[0,ar]) for ar in [ dx, dy, dz ] ])
    I, J, K = meshgrid(*[ np.arange(n) for n in ijk_shape ])

    # Points and cells
    points = [ [ x, y, z ] for x, y, z in zip(X, Y, Z) ]
    cells = [ [ np.ravel_multi_index(vertex, xyz_shape, order = "F")
                for vertex in mesh_vertices(i, j, k) ]
                for i, j, k in zip(I, J, K) ]
    return np.array(points), { "hexahedron": np.array(cells) }


def _grid_2d(dx, dy):
    """
    Generate 2D cartesian grid.
    """
    # Internal functions
    def meshgrid(x, y, indexing = "ij", order = "F"):
        X, Y = np.meshgrid(x, y, indexing = indexing)
        return X.ravel(order), Y.ravel(order)
    
    def mesh_vertices(i, j):
        return [
            [ i, j ],
            [ i+1, j ],
            [ i+1, j+1 ],
            [ i, j+1 ],
        ]

    # Grid
    nx, ny = len(dx), len(dy)
    xy_shape = [ nx+1, ny+1 ]
    ij_shape = [ nx, ny ]
    X, Y = meshgrid(*[ np.cumsum(np.r_[0,ar]) for ar in [ dx, dy ] ])
    I, J = meshgrid(*[ np.arange(n) for n in ij_shape ])

    # Points and cells
    points = [ [ x, y ] for x, y in zip(X, Y) ]
    cells = [ [ np.ravel_multi_index(vertex, xy_shape, order = "F")
                for vertex in mesh_vertices(i, j) ]
                for i, j in zip(I, J) ]
    return np.array(points), { "quad": np.array(cells) }