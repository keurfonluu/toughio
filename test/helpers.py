import os
import tempfile

import numpy

import toughio

numpy.random.seed(42)

tet_mesh = toughio.Mesh(
    points=numpy.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.5, 0.5, 0.5],
        ]
    ),
    cells=[("tetra", numpy.array([[0, 1, 2, 4], [0, 2, 3, 4]]))],
    point_data={"a": numpy.random.rand(5), "b": numpy.random.rand(5)},
    cell_data={"c": numpy.random.rand(2), "d": numpy.random.rand(2)},
)

hex_mesh = toughio.Mesh(
    points=numpy.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    ),
    cells=[("hexahedron", numpy.array([[0, 1, 2, 3, 4, 5, 6, 7]]))],
    point_data={"a": numpy.random.rand(8), "b": numpy.random.rand(8)},
    cell_data={"c": numpy.random.rand(1), "d": numpy.random.rand(1)},
)

hybrid_mesh = toughio.Mesh(
    points=numpy.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
            [0.5, 0.5, 1.5],
            [0.0, 0.5, 1.5],
            [1.0, 0.5, 1.5],
            [2.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [-1.0, 1.0, 0.0],
        ]
    ),
    cells=[
        ("hexahedron", numpy.array([[0, 1, 2, 3, 4, 5, 6, 7]])),
        ("pyramid", numpy.array([[4, 5, 6, 7, 8]])),
        ("tetra", numpy.array([[4, 8, 7, 9], [5, 6, 8, 10]])),
        ("wedge", numpy.array([[1, 11, 5, 2, 12, 6], [13, 0, 4, 14, 3, 7]])),
    ],
    point_data={"a": numpy.random.rand(15), "b": numpy.random.rand(15)},
    cell_data={"c": numpy.random.rand(6), "d": numpy.random.rand(6)},
)

output_eleme = [
    toughio.Output(
        "element",
        None,
        numpy.random.rand(),
        numpy.array(["AAA0{}".format(i) for i in range(10)]),
        {
            "X": numpy.random.rand(10),
            "Y": numpy.random.rand(10),
            "Z": numpy.random.rand(10),
            "PRES": numpy.random.rand(10),
            "TEMP": numpy.random.rand(10),
        },
    )
    for _ in range(3)
]

output_conne = [
    toughio.Output(
        "connection",
        None,
        numpy.random.rand(),
        numpy.array([["AAA0{}".format(i), "AAA0{}".format(i)] for i in range(10)]),
        {
            "X": numpy.random.rand(10),
            "Y": numpy.random.rand(10),
            "Z": numpy.random.rand(10),
            "HEAT": numpy.random.rand(10),
            "FLOW": numpy.random.rand(10),
        },
    )
    for _ in range(3)
]


def tempdir(filename=None):
    temp_dir = tempfile.mkdtemp()
    return os.path.join(temp_dir, filename) if filename else temp_dir


def write_read(filename, obj, writer, reader, writer_kws=None, reader_kws=None):
    writer_kws = writer_kws if writer_kws else {}
    reader_kws = reader_kws if reader_kws else {}

    filepath = tempdir(filename)
    if obj is not None:
        writer(filepath, obj, **writer_kws)
    else:
        writer(filepath, **writer_kws)

    return reader(filepath, **reader_kws)


def random_string(n):
    import random
    from string import ascii_lowercase

    return "".join(random.choice(ascii_lowercase) for _ in range(n))


def allclose_dict(a, b, atol=1.0e-8):
    for k, v in a.items():
        if v is not None:
            assert numpy.allclose(v, b[k], atol=atol)
        else:
            assert b[k] is None


def allclose_mesh(mesh_ref, mesh):
    assert numpy.allclose(mesh_ref.points, mesh.points)

    for i, cell in enumerate(mesh_ref.cells):
        assert cell.type == mesh.cells[i].type
        assert numpy.allclose(cell.data, mesh.cells[i].data)

    if mesh.point_data:
        for k, v in mesh_ref.point_data.items():
            assert numpy.allclose(v, mesh.point_data[k])

    if mesh.cell_data:
        for k, v in mesh_ref.cell_data.items():
            assert numpy.allclose(v, mesh.cell_data[k])


def allclose_output(output_ref, output):
    assert output_ref.type == output.type
    assert numpy.allclose(output_ref.time, output.time)
    assert output_ref.labels.tolist() == output_ref.labels.tolist()
    allclose_dict(output_ref.data, output.data)
