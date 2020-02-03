from .__about__ import (
    __version__,
    __author__,
    __author_email__,
    __website__,
    __license__,
)

from . import mesh

from .mesh import Mesh

from .io import (
    read_input,
    write_input,
    read_output,
)

__all__ = [
    "Mesh",
    "mesh",
    "read_input",
    "write_input",
    "read_output",
    "__version__",
    "__author__",
    "__author_email__",
    "__website__",
    "__license__",
]