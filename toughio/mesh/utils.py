# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from __future__ import division, with_statement, unicode_literals

import logging

import numpy as np

from copy import deepcopy
from . import meshio

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


def build_connectivity(mesh, leaf_size = 40, n_jobs = 1):
    """
    Build mesh connectivity assuming conformity and that points and cells
    are uniquely defined in mesh (use prune_duplicates otherwise). In 3D,
    non-conformal meshes are handled if and only if connected cells share
    at least 3 common points (1 quad with 2 triangle faces).

    Scikit-learn BallTree algorithm is used to build cell neighborhood
    topology following a custom distance function.

    Parameters
    ----------
    mesh : Mesh
        Input mesh.
    leaf_size : int, optional, default 40
        Number of points at which to switch to brute-force.
    n_jobs : int, optional, default 1
        Number of processes to create to query cell connectivity in
        parallel (requires joblib).

    Note
    ----
    Custom distance functions for BallTree are reaaaaaaally slow.
    - https://github.com/scikit-learn/scikit-learn/issues/6256
    - https://blog.sicara.com/fast-custom-knn-sklearn-cython-de92e5a325c
    """
    from sklearn.neighbors import BallTree
    from numba import njit, int32, float64
    from joblib import Parallel, delayed

    # Custom distance function for BallTree neighboring algorithm
    @njit(int32(float64[:], float64[:], int32), nogil = True)
    def distance(x, y, ndim):
        """
        Return 0 if connected 1 otherwise given that:
        - 2D neighboring cells have at least 2 common corner points
        - 3D neighboring cells have at least 3 common corner points
        Apply threshold to ignore the cell itself (all its points are in
        common).
        """
        xs, ys = set(x), set(y)
        return 0 if ndim <= len(xs.intersection(ys)) < min(len(xs), len(ys)) else 1
    
    # Determine if mesh is 2D or 3D
    ndim = 2 if any([ k in mesh.cells.keys() for k in [ "triangle", "quad" ] ]) else 3

    # Maximum number of connections per cell
    ncon_max = {
        "triangle": 3,
        "quad": 4,
        "tetra": 4,
        "pyramid": 6,
        "wedge": 8,
        "hexahedron": 12,
    }
    k_max = max([ ncon_max[k] for k in mesh.cells.keys() ])

    # Maximum number of corner points in mesh
    nvert = {
        "triangle": 3,
        "quad": 4,
        "tetra": 4,
        "pyramid": 5,
        "wedge": 6,
        "hexahedron": 8,
    }
    nvert_max = max([ nvert[k] for k in mesh.cells.keys() ])

    # If hybrid mesh, duplicate last corner point
    corners = np.array([
        np.r_[corner,[ corner[-1] ] * ( nvert_max - nvert[k] )]
        for k, v in mesh.cells.items() for corner in v
    ])

    # BallTree neighboring algorithm
    tree = BallTree(
        corners,
        leaf_size = leaf_size,
        metric = "pyfunc",
        func = distance,
        ndim = ndim,
    )

    k = min(k_max, len(corners))
    if n_jobs and n_jobs > 1:
        # Split corners for parallel query
        nrow = corners.shape[0] // n_jobs
        par_corners = corners[:n_jobs*nrow].reshape(
            (n_jobs, nrow, corners.shape[1]),
        ).tolist()
        if corners[n_jobs*nrow:].size:
            par_corners[-1].extend(corners[n_jobs*nrow:].tolist())

        with Parallel(n_jobs = n_jobs) as parallel:
            dist_idx = parallel(delayed(tree.query)(
                    np.array(corner),
                    k = k,
                    dualtree = True,
                ) for corner in par_corners
            )
        
        # Reconstruct arrays from parallel results
        dist = [ dd for d in dist_idx for dd in d[0] ]
        idx = [ ii for i in dist_idx for ii in i[1] ]
    else:
        dist, idx = tree.query(
            corners,
            k = k,
            dualtree = True,
        )

    # Connected cells have 0 distance values, others have 1
    conn = [ sorted([ i for i in ma if isinstance(i, np.int32) ])
                for ma in np.ma.array(idx, mask = dist, dtype = np.int32) ]
    
    # Reorganize output
    meshio_types = [ [ k ] * len(v) for k, v in mesh.cells.items() ]
    meshio_types = [ m for mtype in meshio_types for m in mtype ]
    meshio_index = np.concatenate(
        [ np.arange(len(v), dtype = int) for v in mesh.cells.values() ]
    ).tolist()
    out = {
        k: { i: { kk: [] for kk in mesh.cells.keys() }
        for i in range(len(v)) } for k, v in mesh.cells.items()
    }
    counter = {
        k: { i: { kk: 0 for kk in mesh.cells.keys() }
        for i in range(len(v)) } for k, v in mesh.cells.items()
    }
    for co, mt, mi in zip(conn, meshio_types, meshio_index):
        for c in co:
            out[mt][mi][meshio_types[c]].append(meshio_index[c])
            counter[mt][mi][meshio_types[c]] += 1

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