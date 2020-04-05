import numpy
import pytest

import toughio


@pytest.mark.parametrize("ndim", [2, 3])
def test_triangulate(ndim):
    points = numpy.random.rand(100, ndim)
    mesh = toughio.meshmaker.triangulate(points)
    assert numpy.allclose(points, mesh.points)
    assert mesh.cells[0].type == ("triangle" if ndim == 2 else "tetra")


def test_voxelize():
    points = numpy.random.rand(numpy.random.randint(10) + 1)
    mesh = toughio.meshmaker.voxelize(points)
    assert numpy.allclose(numpy.argsort(points), numpy.argsort(mesh.centers[:, 0]))
