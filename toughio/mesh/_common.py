import numpy

import meshio

from string import ascii_uppercase

__all__ = [
    "vtk_to_meshio_type",
    "meshio_to_vtk_type",
    "vtk_type_to_numnodes",
    "meshio_type_to_ndim",
    "meshio_data",
    "get_meshio_version",
    "labeler",
]


vtk_to_meshio_type = {
    0: "empty",
    1: "vertex",
    # 2: "poly_vertex",
    3: "line",
    # 4: "poly_line",
    5: "triangle",
    # 6: "triangle_strip",
    7: "polygon",
    # 8: "pixel",
    9: "quad",
    10: "tetra",
    # 11: "voxel",
    12: "hexahedron",
    13: "wedge",
    14: "pyramid",
    15: "penta_prism",
    16: "hexa_prism",
    21: "line3",
    22: "triangle6",
    23: "quad8",
    24: "tetra10",
    25: "hexahedron20",
    26: "wedge15",
    27: "pyramid13",
    28: "quad9",
    29: "hexahedron27",
    30: "quad6",
    31: "wedge12",
    32: "wedge18",
    33: "hexahedron24",
    34: "triangle7",
    35: "line4",
    #
    # 60: VTK_HIGHER_ORDER_EDGE,
    # 61: VTK_HIGHER_ORDER_TRIANGLE,
    # 62: VTK_HIGHER_ORDER_QUAD,
    # 63: VTK_HIGHER_ORDER_POLYGON,
    # 64: VTK_HIGHER_ORDER_TETRAHEDRON,
    # 65: VTK_HIGHER_ORDER_WEDGE,
    # 66: VTK_HIGHER_ORDER_PYRAMID,
    # 67: VTK_HIGHER_ORDER_HEXAHEDRON,
}
meshio_to_vtk_type = {v: k for k, v in vtk_to_meshio_type.items()}


vtk_type_to_numnodes = {
    0: 0,       # empty
    1: 1,       # vertex
    3: 2,       # line
    5: 3,       # triangle
    9: 4,       # quad
    10: 4,      # tetra
    12: 8,      # hexahedron
    13: 6,      # wedge
    14: 5,      # pyramid
    15: 10,     # penta_prism
    16: 12,     # hexa_prism
    21: 3,      # line3
    22: 6,      # triangle6
    23: 8,      # quad8
    24: 10,     # tetra10
    25: 20,     # hexahedron20
    26: 15,     # wedge15
    27: 13,     # pyramid13
    28: 9,      # quad9
    29: 27,     # hexahedron27
    30: 6,      # quad6
    31: 12,     # wedge12
    32: 18,     # wedge18
    33: 24,     # hexahedron24
    34: 7,      # triangle7
    35: 4,      # line4
}


meshio_type_to_ndim = {k: 3 for k in meshio_to_vtk_type.keys()}
meshio_type_to_ndim.update({
    "empty": 0,
    "vertex": 1,
    "line": 2,
    "triangle": 2,
    "polygon": 2,
    "quad": 2,
})


meshio_data = {
    "material",
    "avsucd:material",
    "flac3d:zone",
    "gmsh:physical",
    "medit:ref",
}


alpha = list(ascii_uppercase)
numer = ["{:0>2}".format(i) for i in range(100)]
nomen = ["{:1}".format(i + 1) for i in range(9)] + alpha


def get_meshio_version():
    """
    Return ``meshio`` version as a tuple.

    Returns
    -------
    tuple
        ``meshio`` version as tuple (major, minor, patch).
    """
    return tuple(int(i) for i in meshio.__version__.split("."))


def labeler(i):
    """
    Return five-character long cell labels following:
    - 1st: from A to Z
    - 2nd and 3rd: from 1 to 9 then A to Z
    - 4th and 5th: from 00 to 99
    Incrementation is performed from right to left.

    Parameters
    ----------
    i : int
        Cell general index in mesh.

    Returns
    -------
    str
        Label for cell `i`.

    Note
    ----
    Currently support up to 3,185,000 different cells.
    """
    q1, r1 = divmod(i, len(numer))
    q2, r2 = divmod(q1, len(nomen))
    q3, r3 = divmod(q2, len(nomen))
    _, r4 = divmod(q3, len(nomen))
    return "".join([alpha[r4], nomen[r3], nomen[r2], numer[r1]])