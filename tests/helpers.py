import os
import tempfile
from collections.abc import Sequence

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
    cell_data={"c": np.random.rand(2), "material": np.ones(2, dtype=np.int64)},
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
    cell_data={"c": np.random.rand(1), "material": np.ones(1, dtype=np.int64)},
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
    cell_data={"c": np.random.rand(6), "material": np.ones(6, dtype=np.int64)},
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


def random_label(label_length=5):
    n = label_length - 3
    fmt = f"{{:0{n}d}}"

    return random_string(3) + fmt.format(np.random.randint(10**n))


def allclose(x, y, atol=1.0e-8, ignore_keys=None, ignore_none=False):
    ignore_keys = ignore_keys if ignore_keys is not None else []

    if isinstance(x, dict):
        assert isinstance(y, dict)

        for k, v in x.items():
            if k in ignore_keys:
                continue

            if ignore_none and v is None:
                continue

            try:
                assert allclose(v, y[k], atol=atol, ignore_none=ignore_none)

            except KeyError as e:
                print("x =", v, "\ny =", y[k], "\n")
                raise KeyError(e)

    else:
        try:
            if isinstance(x, toughio.Mesh):
                assert isinstance(y, toughio.Mesh)

                assert allclose(x.points, y.points, atol=atol)
                assert allclose(x.cells, y.cells, atol=atol)

                if x.point_data:
                    assert allclose(x.point_data, y.point_data, atol=atol)

                if x.cell_data:
                    assert allclose(x.cell_data, y.cell_data, atol=atol)

            elif isinstance(x, toughio.Output):
                assert isinstance(y, toughio.Output)

                assert allclose(x.type, y.type, atol=atol)
                assert allclose(x.time, y.time, atol=atol)
                assert allclose(x.data, y.data, atol=atol)

                if np.ndim(x.labels) != 0:
                    assert allclose(x.labels, y.labels, atol=atol)

            # str is a Sequence
            elif isinstance(x, (str, type(None))):
                assert x == y

            elif isinstance(x, (Sequence, np.ndarray)):
                for xx, yy in zip(x, y):
                    assert allclose(xx, yy, atol=atol, ignore_none=ignore_none)

            else:
                assert np.allclose(x, y, atol=atol)

        except Exception as e:
            print("x =", x, "\ny =", y, "\n")
            raise Exception(e)

    return True


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
