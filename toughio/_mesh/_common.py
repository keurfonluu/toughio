import logging

import meshio
import numpy

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


meshio_type_to_ndim = {k: 3 for k in meshio_to_vtk_type.keys()}
meshio_type_to_ndim.update(
    {"empty": 0, "vertex": 1, "line": 2, "triangle": 2, "polygon": 2, "quad": 2}
)


def get_meshio_version():
    """
    Return :mod:`meshio` version as a tuple.

    Returns
    -------
    tuple
        :mod:`meshio` version as tuple (major, minor, patch).

    """
    return tuple(int(i) for i in meshio.__version__.split("."))


def get_old_meshio_cells(cells, cell_data=None):
    """
    Return old-style cells and cell_data (meshio < 4.0.0).

    Parameters
    ----------
    cells : list of namedtuple (type, data)
        New-style cells.
    cell_data : dict or None, optional, default None
        New-style cell data.

    Returns
    -------
    dict
        Old-style cells.
    dict
        Old-style cell data (only if `cell_data` is not None).

    """
    old_cells, cell_blocks = {}, {}
    for ic, c in enumerate(cells):
        if c.type not in old_cells.keys():
            old_cells[c.type] = [c.data]
            cell_blocks[c.type] = [ic]
        else:
            old_cells[c.type].append(c.data)
            cell_blocks[c.type].append(ic)
    old_cells = {k: numpy.concatenate(v) for k, v in old_cells.items()}

    if cell_data is not None:
        old_cell_data = (
            {
                cell_type: {
                    k: numpy.concatenate([cell_data[k][i] for i in iblock])
                    for k in cell_data.keys()
                }
                for cell_type, iblock in cell_blocks.items()
            }
            if cell_data
            else {}
        )
        return old_cells, old_cell_data
    else:
        return old_cells


def get_new_meshio_cells(cells, cell_data=None):
    """
    Return new-style cells and cell_data (meshio >= 4.0.0).

    Parameters
    ----------
    cells : dict
        Old-style cells.
    cell_data : dict or None, optional, default None
        Old-style cell data.

    Returns
    -------
    list of namedtuple (type, data)
        New-style cells.
    dict
        New-style cell data (only if `cell_data` is not None).

    """
    from ._mesh import CellBlock

    new_cells = [CellBlock(k, v) for k, v in cells.items()]

    if cell_data is not None:
        labels = numpy.unique([kk for k, v in cell_data.items() for kk in v.keys()])
        new_cell_data = {k: [] for k in labels}
        for k in new_cell_data.keys():
            for kk in cells.keys():
                new_cell_data[k].append(cell_data[kk][k])
        return new_cells, new_cell_data
    else:
        return new_cells


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
        bins = 3185000 * 10 ** numpy.arange(5, dtype=numpy.int64) + 1
        label_length = numpy.digitize(n_cells, bins) + 5
        if label_length > 5:
            logging.warning("Cell labels are {}-character long.".format(label_length))

    n = label_length - 3
    fmt = "{{:0>{}}}".format(n)
    alpha = numpy.array(list(ascii_uppercase))
    numer = numpy.array([fmt.format(i) for i in range(10 ** n)])
    nomen = numpy.concatenate((["{:1}".format(i + 1) for i in range(9)], alpha))

    q1, r1 = numpy.divmod(numpy.arange(n_cells), numer.size)
    q2, r2 = numpy.divmod(q1, nomen.size)
    q3, r3 = numpy.divmod(q2, nomen.size)
    _, r4 = numpy.divmod(q3, nomen.size)

    iterables = (alpha[r4], nomen[r3], nomen[r2], numer[r1])
    return numpy.array(["".join(name) for name in zip(*iterables)])


def cell_data_to_point_data(cell_data, points, weights):
    """Interpolate cell data to point data."""
    point_data = {}
    for k, v in cell_data.items():
        point_data[k] = numpy.array([numpy.average(v[p], weights=w) for p, w in zip(points, weights)])
    
    for k in point_data.keys():
        cell_data.pop(k, None)

    return point_data
