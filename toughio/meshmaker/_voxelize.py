import numpy

from ._structured_grid import structured_grid

__all__ = [
    "voxelize",
]


def voxelize(points, origin, material="dfalt"):
    """
    Generate a 3D non-uniform structured grid from cloud points.

    Input points must form a non-uniform structured grid.

    Parameters
    ----------
    points : array_like
        Cooordinates of points.
    origin : array_like
        Origin point coordinate.
    material : str, optional, default 'dfalt'
        Default material name.

    Returns
    -------
    toughio.Mesh
        Output non-uniform structured mesh.

    """
    def voronoi1d(x, x0):
        """1D Voronoi tessellation."""
        x = numpy.sort(x)
        if x0 >= x[0]:
            raise ValueError()

        vor = [x0]
        for xx in x:
            vor.append(2 * xx - vor[-1])

        return vor

    if not isinstance(points, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if numpy.ndim(points) != 2:
        raise ValueError()

    x, y, z = numpy.transpose(points)
    x = numpy.unique(x)
    y = numpy.unique(y)
    z = numpy.unique(z)
    if x.size * y.size * z.size != len(points):
        raise ValueError("Input points do not form a structured grid.")

    x0, y0, z0 = origin
    x = voronoi1d(x, x0)
    y = voronoi1d(y, y0)
    z = voronoi1d(z, z0)
    dx = numpy.diff(x)
    dy = numpy.diff(y)
    dz = numpy.diff(z)
    mesh = structured_grid(dx, dy, dz, origin, material)

    return mesh
