import numpy

from .._mesh import Mesh
from ._structured_grid import structured_grid

__all__ = [
    "cylindric_grid",
]


class CylindricMesh(Mesh):
    def __init__(self, dr, dz, *args, **kwargs):
        """
        Cylindric mesh.

        This class is only intended to be used as output of :func:`cylindric_grid`.

        Note
        ----
        This class inherits from :class:`toughio.Mesh` but overwrites how face areas
        and volumes are calculated.

        """
        super(CylindricMesh, self).__init__(*args, **kwargs)
        self._dr = dr
        self._dz = dz

    def _get_areas_heights(self):
        """Return areas and heights of cells in mesh."""
        nr, nz = len(self._dr), len(self._dz)
        r2 = numpy.cumsum(self._dr) ** 2
        areas = (
            numpy.tile(numpy.concatenate(([r2[0]], r2[1:] - r2[:-1])), nz) * numpy.pi
        )
        heights = numpy.tile(self._dz[:, None], nr).ravel()

        return areas, heights

    @property
    def face_areas(self):
        """Areas of faces in mesh."""
        nz = len(self._dz)
        dr = numpy.concatenate(([0.0], self._dr))
        perimeters_in = numpy.tile(numpy.cumsum(dr[:-1]), nz) * 2.0 * numpy.pi
        perimeters_out = numpy.tile(numpy.cumsum(dr[1:]), nz) * 2.0 * numpy.pi
        areas, heights = self._get_areas_heights()
        sections = numpy.tile(self._dr, nz) * heights

        return numpy.transpose(
            [
                areas,
                areas,
                sections,
                perimeters_out * heights,
                sections,
                perimeters_in * heights,
            ]
        )

    @property
    def volumes(self):
        """Volumes of cell in mesh."""
        areas, heights = self._get_areas_heights()
        return areas * heights


def cylindric_grid(dr, dz, origin_z=None, material="dfalt"):
    """
    Generate a cylindric mesh as a radial XZ structured grid.

    Parameters
    ----------
    dr : array_like
        Grid spacing along X axis.
    dz : array_like
        Grid spacing along Z axis.
    origin_z : scalar, optional, default None
        Depth of origin point.
    material : str, optional, default 'dfalt'
        Default material name.

    Returns
    -------
    toughio.Mesh
        Output cylindric mesh.

    """
    if not isinstance(dr, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if not isinstance(dz, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if not (origin_z is None or isinstance(origin_z, (int, float))):
        raise TypeError()
    if not isinstance(material, str):
        raise TypeError()

    dr = numpy.asarray(dr)
    dz = numpy.asarray(dz)
    if not (dr > 0.0).all():
        raise ValueError()
    if not (dz > 0.0).all():
        raise ValueError()
    origin_z = origin_z if origin_z is not None else -dz.sum()

    mesh = structured_grid(
        dr, [1.0], dz, origin=[0.0, -0.5, origin_z], material=material
    )

    return CylindricMesh(
        dr,
        dz,
        points=mesh.points,
        cells=mesh.cells,
        point_data=mesh.point_data,
        cell_data=mesh.cell_data,
        field_data=mesh.field_data,
    )
