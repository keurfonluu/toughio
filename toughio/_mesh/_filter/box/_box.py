import numpy as np

from .._helpers import register

__all__ = [
    "filter_",
]


def filter_(mesh, x0=None, y0=None, z0=None, dx=None, dy=None, dz=None):
    """Box filter."""
    xmin = x0 if x0 is not None else -np.inf
    ymin = y0 if y0 is not None else -np.inf
    zmin = z0 if z0 is not None else -np.inf

    xmax = xmin + dx if dx else np.inf
    ymax = ymin + dy if dy else np.inf
    zmax = zmin + dz if dz else np.inf

    x, y, z = mesh.centers.T
    mask_x = np.logical_and(x >= xmin, x <= xmax)
    mask_y = np.logical_and(y >= ymin, y <= ymax)
    mask_z = np.logical_and(z >= zmin, z <= zmax)
    mask = np.logical_and(np.logical_and(mask_x, mask_y), mask_z)

    return np.arange(mesh.n_cells)[mask]


register("box", filter_)
