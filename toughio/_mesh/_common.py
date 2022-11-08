import logging

import numpy as np

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
    0: 0,  # empty
    1: 1,  # vertex
    3: 2,  # line
    5: 3,  # triangle
    9: 4,  # quad
    10: 4,  # tetra
    12: 8,  # hexahedron
    13: 6,  # wedge
    14: 5,  # pyramid
    15: 10,  # penta_prism
    16: 12,  # hexa_prism
    21: 3,  # line3
    22: 6,  # triangle6
    23: 8,  # quad8
    24: 10,  # tetra10
    25: 20,  # hexahedron20
    26: 15,  # wedge15
    27: 13,  # pyramid13
    28: 9,  # quad9
    29: 27,  # hexahedron27
    30: 6,  # quad6
    31: 12,  # wedge12
    32: 18,  # wedge18
    33: 24,  # hexahedron24
    34: 7,  # triangle7
    35: 4,  # line4
}


meshio_type_to_ndim = {k: 3 for k in meshio_to_vtk_type}
meshio_type_to_ndim.update(
    {"empty": 0, "vertex": 1, "line": 2, "triangle": 2, "polygon": 2, "quad": 2}
)


def labeler(n_cells, label_length=None):
    """
    Return an array of `label_length`-character long cell labels.

    Parameters
    ----------
    n_cells : int
        Number of cells.
    label_length : int or None, optional, default None
        Number of characters in cell labels.

    Returns
    -------
    array_like
        Array of labels of size `n_cells`.

    Note
    ----
    `label_length` corresponds to option MOP2(2).

    """
    from string import ascii_uppercase

    if not label_length:
        bins = 3185000 * 10 ** np.arange(5, dtype=np.int64) + 1
        label_length = np.digitize(n_cells, bins) + 5
        if label_length > 5:
            logging.warning(f"Cell labels are {label_length}-character long.")

    n = label_length - 3
    fmt = f"{{: >{n}}}"
    alpha = np.array(list(ascii_uppercase))
    numer = np.array([fmt.format(i) for i in range(10**n)])
    nomen = np.concatenate(([f"{i + 1:1}" for i in range(9)], alpha))

    q1, r1 = np.divmod(np.arange(n_cells), numer.size)
    q2, r2 = np.divmod(q1, nomen.size)
    q3, r3 = np.divmod(q2, nomen.size)
    _, r4 = np.divmod(q3, nomen.size)

    iterables = (alpha[r4], nomen[r3], nomen[r2], numer[r1])
    return np.array(["".join(name) for name in zip(*iterables)])


def interpolate_data(data, entities, weights=None):
    """Interpolate input data."""
    return {
        k: (
            np.array([np.mean(v[e]) for e in entities])
            if not weights
            else np.array(
                [np.average(v[e], weights=w) for e, w in zip(entities, weights)]
            )
        )
        for k, v in data.items()
    }
