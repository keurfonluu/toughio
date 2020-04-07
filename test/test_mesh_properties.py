import os

import numpy

import toughio


def test_mesh():
    """Reference values are calculated in FLAC3D."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "all_cell_types.f3grid")
    mesh = toughio.read_mesh(filename)

    volumes = mesh.volumes.sum()
    assert numpy.allclose(volumes, 1.7083333333333344)

    face_areas = sum(face.sum() for face in mesh.face_areas)
    assert numpy.allclose(face_areas, 39.16535341331142)

    face_normals = sum(numpy.abs(face).sum() for face in mesh.face_normals)
    assert numpy.allclose(face_normals, 719.3660094744944)

    connections = mesh.connections.sum()
    assert numpy.allclose(connections, 25353)
