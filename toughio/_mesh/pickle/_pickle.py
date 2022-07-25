import pickle

from ..._common import open_file

__all__ = [
    "read",
    "write",
]


def read(filename):
    """
    Import pickled :class:`toughio.Mesh`.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.

    Returns
    -------
    toughio.Mesh
        Output mesh.

    """
    with open_file(filename, "rb") as f:
        mesh = pickle.load(f)

    return mesh


def write(filename, mesh, protocol=pickle.HIGHEST_PROTOCOL):
    """
    Pickle :class:`toughio.Mesh`.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    mesh : toughio.Mesh
        Mesh to pickle.
    protocol : integer, optional, default `pickle.HIGHEST_PROTOCOL`
        :mod:`pickle` protocol version.

    """
    with open_file(filename, "wb") as f:
        pickle.dump(mesh, f, protocol=protocol)
