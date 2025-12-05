import os
import pytest
import random
import tempfile
from collections.abc import Sequence

import numpy as np

import toughio


class Helpers:
    def allclose(self, x, y, atol=1.0e-8, ignore_keys=None, ignore_none=False):
        ignore_keys = ignore_keys if ignore_keys is not None else []

        if isinstance(x, dict):
            assert isinstance(y, dict)

            for k, v in x.items():
                if k in ignore_keys:
                    continue

                if ignore_none and v is None:
                    continue

                try:
                    assert self.allclose(v, y[k], atol=atol, ignore_none=ignore_none)

                except KeyError as e:
                    print("x =", v, "\ny =", y[k], "\n")
                    raise KeyError(e)

        else:
            try:
                if isinstance(x, toughio.Mesh):
                    assert isinstance(y, toughio.Mesh)

                    assert self.allclose(x.points, y.points, atol=atol)
                    assert self.allclose(x.cells, y.cells, atol=atol)

                    if x.point_data:
                        assert self.allclose(x.point_data, y.point_data, atol=atol)

                    if x.cell_data:
                        assert self.allclose(x.cell_data, y.cell_data, atol=atol)

                elif isinstance(x, (toughio.ElementOutput, toughio.ConnectionOutput)):
                    assert isinstance(
                        y, (toughio.ElementOutput, toughio.ConnectionOutput)
                    )

                    assert self.allclose(x.time, y.time, atol=atol)
                    assert self.allclose(x.data, y.data, atol=atol)

                    if np.ndim(x.labels) != 0:
                        assert self.allclose(x.labels, y.labels, atol=atol)

                # str is a Sequence
                elif isinstance(x, (str, type(None))):
                    assert x == y

                elif isinstance(x, (Sequence, np.ndarray)):
                    assert len(x) == len(y)
                    
                    for xx, yy in zip(x, y):
                        assert self.allclose(xx, yy, atol=atol, ignore_none=ignore_none)

                else:
                    assert np.allclose(x, y, atol=atol)

            except Exception as e:
                print("x =", x, "\ny =", y, "\n")
                raise Exception(e)

        return True

    def random_label(self, label_length=5):
        n = label_length - 3
        fmt = f"{{:0{n}d}}"

        return self.random_string(3) + fmt.format(np.random.randint(10**n))

    @staticmethod
    def random_string(n):
        from string import ascii_lowercase

        return "".join(random.choice(ascii_lowercase) for _ in range(n))

    @staticmethod
    def tempdir(filename=None):
        temp_dir = tempfile.mkdtemp()
        return os.path.join(temp_dir, filename) if filename else temp_dir

    def write_read(
        self, filename, obj, writer, reader, writer_kws=None, reader_kws=None
    ):
        writer_kws = writer_kws if writer_kws else {}
        reader_kws = reader_kws if reader_kws else {}

        filepath = self.tempdir(filename)
        if obj is not None:
            writer(filepath, obj, **writer_kws)
        else:
            writer(filepath, **writer_kws)

        return reader(filepath, **reader_kws)


@pytest.fixture
def helpers():
    return Helpers()


@pytest.fixture(scope="module", autouse=True)
def set_random_seed():
    np.random.seed(42)
    random.seed(42)
