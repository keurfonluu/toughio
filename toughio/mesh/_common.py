import meshio

__all__ = [
    "vtk_to_meshio_type",
    "meshio_to_vtk_type",
    "vtk_type_to_numnodes",
    "get_meshio_version",
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


def get_meshio_version():
    return tuple(int(i) for i in meshio.__version__.split("."))