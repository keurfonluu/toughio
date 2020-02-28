import numpy

from ..mesh._mesh import Cells, Mesh

__all__ = [
    "structured_grid",
]


def structured_grid(dx, dy, dz=None, origin=None, material="dfalt"):
    """Generate 2D or 3D non-uniform structured grid.

    Parameters
    ----------
    dx : array_like
        Grid spacing along X axis.
    dy : array_like
        Grid spacing along Y axis.
    dz : array_like or None, optional, default None
        Grid spacing along Z axis. If `None`, generate 2D grid.
    origin : array_like or None, optional, default None
        Origin point coordinate.
    material : str, optional, default 'dfalt'
        Default material name.

    Returns
    -------
    toughio.Mesh
        Output non-uniform structured mesh.

    """
    if not isinstance(dx, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if not isinstance(dy, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if not (dz is None or isinstance(dz, (list, tuple, numpy.ndarray))):
        raise TypeError()
    if not isinstance(material, str):
        raise TypeError()

    if dz is None:
        ndim = 2
        points, cells = _grid_2d(dx, dy)
    else:
        ndim = 3
        points, cells = _grid_3d(dx, dy, dz)

    if not (
        origin is None
        or (isinstance(origin, (list, tuple, numpy.ndarray)) and len(origin) == ndim)
    ):
        raise ValueError()
    origin = (
        numpy.asarray(origin)
        if origin is not None
        else (
            numpy.zeros(ndim) if ndim == 2 else numpy.array([0.0, 0.0, -numpy.sum(dz)])
        )
    )
    points += origin

    points = (
        points if ndim == 3 else numpy.column_stack((points, numpy.zeros(len(points))))
    )

    mesh = Mesh(points, cells)
    mesh.add_cell_data("material", numpy.ones(mesh.n_cells, dtype=int))
    mesh.field_data[material] = numpy.array([1, 3])

    return mesh


def _grid_3d(dx, dy, dz):
    """Generate 3D structured grid."""
    # Internal functions
    def meshgrid(x, y, z, indexing="ij", order="F"):
        X, Y, Z = numpy.meshgrid(x, y, z, indexing=indexing)
        return X.ravel(order), Y.ravel(order), Z.ravel(order)

    def mesh_vertices(i, j, k):
        return [
            [i, j, k],
            [i + 1, j, k],
            [i + 1, j + 1, k],
            [i, j + 1, k],
            [i, j, k + 1],
            [i + 1, j, k + 1],
            [i + 1, j + 1, k + 1],
            [i, j + 1, k + 1],
        ]

    # Grid
    nx, ny, nz = len(dx), len(dy), len(dz)
    xyz_shape = [nx + 1, ny + 1, nz + 1]
    ijk_shape = [nx, ny, nz]
    X, Y, Z = meshgrid(*[numpy.cumsum(numpy.r_[0, ar]) for ar in [dx, dy, dz]])
    I, J, K = meshgrid(*[numpy.arange(n) for n in ijk_shape])

    # Points and cells
    points = [[x, y, z] for x, y, z in zip(X, Y, Z)]
    cells = [
        [
            numpy.ravel_multi_index(vertex, xyz_shape, order="F")
            for vertex in mesh_vertices(i, j, k)
        ]
        for i, j, k in zip(I, J, K)
    ]

    return numpy.array(points), [Cells("hexahedron", numpy.array(cells))]


def _grid_2d(dx, dy):
    """Generate 2D structured grid."""
    # Internal functions
    def meshgrid(x, y, indexing="ij", order="F"):
        X, Y = numpy.meshgrid(x, y, indexing=indexing)
        return X.ravel(order), Y.ravel(order)

    def mesh_vertices(i, j):
        return [
            [i, j],
            [i + 1, j],
            [i + 1, j + 1],
            [i, j + 1],
        ]

    # Grid
    nx, ny = len(dx), len(dy)
    xy_shape = [nx + 1, ny + 1]
    ij_shape = [nx, ny]
    X, Y = meshgrid(*[numpy.cumsum(numpy.r_[0, ar]) for ar in [dx, dy]])
    I, J = meshgrid(*[numpy.arange(n) for n in ij_shape])

    # Points and cells
    points = [[x, y] for x, y in zip(X, Y)]
    cells = [
        [
            numpy.ravel_multi_index(vertex, xy_shape, order="F")
            for vertex in mesh_vertices(i, j)
        ]
        for i, j in zip(I, J)
    ]

    return numpy.array(points), [Cells("quad", numpy.array(cells))]
