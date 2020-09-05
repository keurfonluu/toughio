__all__ = [
    "MeshFilter",
]


_filter_map = {}


def register(filter_name, filter_):
    """Register a new filter."""
    _filter_map[filter_name] = filter_


class MeshFilter(object):
    def __init__(self, mesh):
        """
        Mesh filter.

        Parameters
        ----------
        mesh : toughio.Mesh
            Mesh to filter.

        """
        self._mesh = mesh

    def __call__(self, filter_="box", **kwargs):
        """
        Filter mesh.

        Parameters
        ----------
        filter_ : str, optional, default 'box'
            Filter method.

        Returns
        -------
        array_like
            Indices of cells filtered.

        """
        return _filter_map[filter_](self._mesh, **kwargs)

    def box(self, x0=None, y0=None, z0=None, dx=None, dy=None, dz=None):
        """
        Box filter.

        Parameters
        ----------
        x0 : scalar or None, optional, default None
            Minimum value in X direction.
        y0 : scalar or None, optional, default None
            Minimum value in Y direction.
        z0 : scalar or None, optional, default None
            Minimum value in Z direction.
        dx : scalar or None, optional, default None
            Box length in X direction.
        dy : scalar or None, optional, default None
            Box length in Y direction.
        dz : scalar or None, optional, default None
            Box length in Z direction.

        Returns
        -------
        array_like
            Indices of cells within the domain defined by the box.

        """
        return self(filter_="box", x0=x0, y0=y0, z0=z0, dx=dx, dy=dy, dz=dz)
