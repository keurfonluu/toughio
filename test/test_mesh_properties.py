import os

import helpers
import numpy as np

import toughio


def test_mesh():
    """Reference values are calculated in FLAC3D."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "all_cell_types.f3grid")
    mesh = toughio.read_mesh(filename)

    volumes = mesh.volumes.sum()
    assert helpers.allclose(volumes, 1.7083333333333344)

    face_areas = sum(face.sum() for face in mesh.face_areas)
    assert helpers.allclose(face_areas, 39.16535341331142)

    face_normals = sum(np.abs(face).sum() for face in mesh.face_normals)
    assert helpers.allclose(face_normals, 719.3660094744944)

    connections = mesh.connections.sum()
    assert helpers.allclose(connections, 25353)


def test_quality():
    dx = np.ones(3)
    dy = np.ones(3)
    dz = np.ones(3)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=np.zeros(3))

    assert helpers.allclose(mesh.qualities, np.ones(mesh.n_cells))
