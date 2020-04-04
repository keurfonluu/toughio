import numpy

import toughio


def test_voxelize():
    points = numpy.random.rand(numpy.random.randint(10) + 1)
    mesh = toughio.meshmaker.voxelize(points)
    assert numpy.allclose(numpy.argsort(points), numpy.argsort(mesh.centers[:, 0]))
