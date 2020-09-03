import numpy

from .._helpers import register

__all__ = [
    "filter_",
]


def filter_(mesh, x0=None, y0=None, z0=None, dx=None, dy=None, dz=None):
    """Box filter."""
    xmin = x0 if x0 else -numpy.inf
    ymin = y0 if y0 else -numpy.inf
    zmin = z0 if z0 else -numpy.inf

    xmax = xmin + dx if dx else numpy.inf
    ymax = ymin + dy if dy else numpy.inf
    zmax = zmin + dz if dz else numpy.inf

    x, y, z = mesh.centers.T
    mask_x = numpy.logical_and(x >= xmin, x <= xmax)
    mask_y = numpy.logical_and(y >= ymin, y <= ymax)
    mask_z = numpy.logical_and(z >= zmin, z <= zmax)
    mask = numpy.logical_and(numpy.logical_and(mask_x, mask_y), mask_z)

    return numpy.arange(mesh.n_cells)[mask]


register("box", filter_)
