from __future__ import with_statement

from .._helpers import register

try:
    import cPickle as pickle
except ImportError:
    import pickle

__all__ = [
    "read",
    "write",
]


def read(filename):
    """
    Import pickled :class:`toughio.Mesh`.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    toughio.Mesh
        Output mesh.

    """
    with open(filename, "rb") as f:
        mesh = pickle.load(f)

    return mesh


def write(filename, mesh, protocol=pickle.HIGHEST_PROTOCOL):
    """
    Pickle :class:`toughio.Mesh`.

    Parameters
    ----------
    filename : str
        Output file name.
    mesh : toughio.Mesh
        Mesh to pickle.
    protocol : integer, optional, default `pickle.HIGHEST_PROTOCOL`
        :mod:`pickle` protocol version.

    """
    with open(filename, "wb") as f:
        pickle.dump(mesh, f, protocol=protocol)


register("pickle", [".pickle", ".pkl"], read, {"pickle": write})
