import meshio

__all__ = [
    "get_meshio_version",
]


def get_meshio_version():
    return tuple(int(i) for i in meshio.__version__.split("."))