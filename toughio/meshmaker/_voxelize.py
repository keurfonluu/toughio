import numpy

from ._structured_grid import structured_grid

__all__ = [
    "voxelize",
]


def voxelize(points, material="dfalt"):
    """Generate a 1D hexahedral mesh from 1D point coordinates.

    Parameters
    ----------
    points : array_like (n_points,)
        Cooordinates of points.
    material : str, optional, default 'dfalt'
        Default material name.

    Returns
    -------
    toughio.Mesh
        Output hexahedral mesh.

    """
    if not isinstance(points, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if numpy.ndim(points) != 1:
        raise ValueError()

    points = numpy.asarray(points)
    idx = numpy.argsort(points)
    dx = 0.5 * (points[idx[1:]] - points[idx[:-1]])
    dx = numpy.concatenate(([dx[0]], dx))
    dy = [0.05 * (points.max() - points.min())]
    dz = dy
    origin = -0.5 * numpy.array([dx[0], dy[0], dz[0]])

    mesh = structured_grid(dx, dy, dz, origin)
    cell_type, cells = mesh.cells[0]
    mesh.cells = [(cell_type, cells[idx])]

    return mesh
