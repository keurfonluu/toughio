import helpers
import numpy as np
import pytest

import toughio


def test_cylindric_grid():
    dr = np.array([1.0, 2.0, 3.0, 4.0])
    dz = np.array([1.0, 2.0, 3.0])
    mesh = toughio.meshmaker.cylindric_grid(dr, dz)

    perimeters = 2.0 * np.pi * dr.cumsum()
    base_areas = np.pi * dr.cumsum() ** 2
    surface_areas = perimeters * dz.sum()
    section_areas = dr.sum() * dz.sum()

    volumes = mesh.volumes.sum()
    assert np.allclose(volumes, base_areas[-1] * dz.sum())

    face_areas_top = np.array(mesh.face_areas)[:, 0].sum()
    assert np.allclose(face_areas_top, base_areas[-1] * len(dz))

    face_areas_bottom = np.array(mesh.face_areas)[:, 1].sum()
    assert np.allclose(face_areas_bottom, base_areas[-1] * len(dz))

    face_areas_section_1 = np.array(mesh.face_areas)[:, 2].sum()
    assert np.allclose(face_areas_section_1, section_areas)

    face_areas_outer = np.array(mesh.face_areas)[:, 3].sum()
    assert np.allclose(face_areas_outer, surface_areas.sum())

    face_areas_section_2 = np.array(mesh.face_areas)[:, 4].sum()
    assert np.allclose(face_areas_section_2, section_areas)

    face_areas_inner = np.array(mesh.face_areas)[:, 5].sum()
    assert np.allclose(face_areas_inner, surface_areas[:-1].sum())


@pytest.mark.parametrize("ndim", [2, 3])
def test_structured_grid(ndim):
    dx = np.array([1.0, 2.0, 3.0, 4.0])
    dy = np.array([1.0, 2.0, 3.0])
    dz = np.array([1.0, 2.0]) if ndim == 3 else None

    origin = np.random.rand(ndim)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=origin)

    assert np.allclose(origin, mesh.points.min(axis=0)[:ndim])

    if ndim == 3:
        volumes_ref = dx.sum() * dy.sum() * dz.sum()
        assert np.allclose(volumes_ref, mesh.volumes.sum())


@pytest.mark.parametrize("ndim", [2, 3])
def test_triangulate(ndim):
    points = np.random.rand(100, ndim)
    mesh = toughio.meshmaker.triangulate(points)

    assert np.allclose(points, mesh.points)
    assert mesh.cells[0].type == ("triangle" if ndim == 2 else "tetra")


def test_voxelize():
    dx = np.array([1.0, 2.0, 3.0, 4.0])
    dy = np.array([1.0, 2.0, 3.0])
    dz = np.array([1.0, 2.0])
    origin = np.random.rand(3)
    mesh_ref = toughio.meshmaker.structured_grid(dx, dy, dz, origin=origin)

    mesh = toughio.meshmaker.voxelize(mesh_ref.centers, origin=origin)
    helpers.allclose_mesh(mesh_ref, mesh)


def test_layer():
    dr = np.array([1.0, 2.0, 3.0, 4.0])
    dz = np.array([1.0, 2.0, 3.0])

    mesh = toughio.meshmaker.cylindric_grid(dr, dz, layer=False)
    mesh_layer = toughio.meshmaker.cylindric_grid(dr, dz, layer=True)

    point = 3.5, 0.0, 1.5
    i1 = mesh.near(point)
    i2 = mesh_layer.near(point)

    assert np.allclose(mesh.volumes[i1], mesh_layer.volumes[i2])
    assert np.allclose(mesh.face_areas[i1], mesh_layer.face_areas[i2])
