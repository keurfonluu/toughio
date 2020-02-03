import numpy

from ..mesh._mesh import Mesh, Cells

__all__ = [
    "meshmaker",
]


def meshmaker(dx, dy, dz = None):
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
    toughio.Mesh
        Output irregular cartesian mesh.
    """
    assert isinstance(dx, (list, tuple, numpy.ndarray))
    assert isinstance(dy, (list, tuple, numpy.ndarray))
    assert dz is None or isinstance(dz, (list, tuple, numpy.ndarray))

    if dz is None:
        points, cells = _grid_2d(dx, dy)
    else:
        points, cells = _grid_3d(dx, dy, dz)

    mesh = Mesh(points, cells)
    mesh.cell_data["material"] = mesh.split(numpy.ones(mesh.n_cells, dtype=int))
    
    return mesh


def _grid_3d(dx, dy, dz):
    """
    Generate 3D cartesian grid.
    """
    # Internal functions
    def meshgrid(x, y, z, indexing = "ij", order = "F"):
        X, Y, Z = numpy.meshgrid(x, y, z, indexing = indexing)
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
    X, Y, Z = meshgrid(*[ numpy.cumsum(numpy.r_[0,ar]) for ar in [ dx, dy, dz ] ])
    I, J, K = meshgrid(*[ numpy.arange(n) for n in ijk_shape ])

    # Points and cells
    points = [ [ x, y, z ] for x, y, z in zip(X, Y, Z) ]
    cells = [ [ numpy.ravel_multi_index(vertex, xyz_shape, order = "F")
                for vertex in mesh_vertices(i, j, k) ]
                for i, j, k in zip(I, J, K) ]

    return numpy.array(points), [Cells("hexahedron", numpy.array(cells))]


def _grid_2d(dx, dy):
    """
    Generate 2D cartesian grid.
    """
    # Internal functions
    def meshgrid(x, y, indexing = "ij", order = "F"):
        X, Y = numpy.meshgrid(x, y, indexing = indexing)
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
    X, Y = meshgrid(*[ numpy.cumsum(numpy.r_[0,ar]) for ar in [ dx, dy ] ])
    I, J = meshgrid(*[ numpy.arange(n) for n in ij_shape ])

    # Points and cells
    points = [ [ x, y ] for x, y in zip(X, Y) ]
    cells = [ [ numpy.ravel_multi_index(vertex, xy_shape, order = "F")
                for vertex in mesh_vertices(i, j) ]
                for i, j in zip(I, J) ]

    return numpy.array(points), [Cells("quad", numpy.array(cells))]



