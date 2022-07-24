import os
import tempfile

import numpy as np

import toughio

np.random.seed(42)

tet_mesh = toughio.Mesh(
    points=np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.5, 0.5, 0.5],
        ]
    ),
    cells=[("tetra", np.array([[0, 1, 2, 4], [0, 2, 3, 4]]))],
    point_data={"a": np.random.rand(5), "b": np.random.rand(5)},
    cell_data={"c": np.random.rand(2), "material": np.ones(2, dtype=int)},
)

hex_mesh = toughio.Mesh(
    points=np.array(
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
    cells=[("hexahedron", np.array([[0, 1, 2, 3, 4, 5, 6, 7]]))],
    point_data={"a": np.random.rand(8), "b": np.random.rand(8)},
    cell_data={"c": np.random.rand(1), "material": np.ones(1, dtype=int)},
)

hybrid_mesh = toughio.Mesh(
    points=np.array(
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
        ("hexahedron", np.array([[0, 1, 2, 3, 4, 5, 6, 7]])),
        ("pyramid", np.array([[4, 5, 6, 7, 8]])),
        ("tetra", np.array([[4, 8, 7, 9], [5, 6, 8, 10]])),
        ("wedge", np.array([[1, 11, 5, 2, 12, 6], [13, 0, 4, 14, 3, 7]])),
    ],
    point_data={"a": np.random.rand(15), "b": np.random.rand(15)},
    cell_data={"c": np.random.rand(6), "material": np.ones(6, dtype=int)},
)

output_eleme = [
    toughio.Output(
        "element",
        None,
        float(time),
        np.array([f"AAA0{i}" for i in range(10)]),
        {
            "X": np.random.rand(10),
            "Y": np.random.rand(10),
            "Z": np.random.rand(10),
            "PRES": np.random.rand(10),
            "TEMP": np.random.rand(10),
        },
    )
    for time in range(3)
]

output_conne = [
    toughio.Output(
        "connection",
        None,
        float(time),
        np.array([[f"AAA0{i}", f"AAA0{i}"] for i in range(10)]),
        {
            "X": np.random.rand(10),
            "Y": np.random.rand(10),
            "Z": np.random.rand(10),
            "HEAT": np.random.rand(10),
            "FLOW": np.random.rand(10),
        },
    )
    for time in range(3)
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


def random_label(label_length):
    n = label_length - 3
    fmt = f"{{:0{n}d}}"

    return random_string(3) + fmt.format(np.random.randint(10 ** n))


def allclose_dict(a, b, atol=1.0e-8):
    for k, v in a.items():
        if v is not None:
            assert np.allclose(v, b[k], atol=atol)
        else:
            assert b[k] is None


def allclose_mesh(mesh_ref, mesh):
    assert np.allclose(mesh_ref.points, mesh.points)

    for i, cell in enumerate(mesh_ref.cells):
        assert cell.type == mesh.cells[i].type
        assert np.allclose(cell.data, mesh.cells[i].data)

    if mesh.point_data:
        for k, v in mesh_ref.point_data.items():
            assert np.allclose(v, mesh.point_data[k])

    if mesh.cell_data:
        for k, v in mesh_ref.cell_data.items():
            assert np.allclose(v, mesh.cell_data[k])


def allclose_output(output_ref, output):
    assert output_ref.type == output.type
    assert np.allclose(output_ref.time, output.time)
    assert output_ref.labels.tolist() == output_ref.labels.tolist()
    allclose_dict(output_ref.data, output.data)


def convert_outputs_labels(outputs, connection=False):
    for output in outputs:
        try:
            if not connection:
                output.labels[:] = toughio.convert_labels(output.labels)

            else:
                labels = toughio.convert_labels(output.labels.ravel())
                output.labels[:] = labels.reshape((labels.size // 2, 2))

        except TypeError:
            pass
