import helpers
import numpy
import pytest

import toughio


def test_cylindric_grid():
    dr = numpy.array([1.0, 2.0, 3.0, 4.0])
    dz = numpy.array([1.0, 2.0, 3.0])
    mesh = toughio.meshmaker.cylindric_grid(dr, dz)

    perimeters = 2.0 * numpy.pi * dr.cumsum()
    base_areas = numpy.pi * dr.cumsum() ** 2
    surface_areas = perimeters * dz.sum()
    section_areas = dr.sum() * dz.sum()

    volumes = mesh.volumes.sum()
    assert numpy.allclose(volumes, base_areas[-1] * dz.sum())

    face_areas_top = numpy.array(mesh.face_areas)[:, 0].sum()
    assert numpy.allclose(face_areas_top, base_areas[-1] * len(dz))

    face_areas_bottom = numpy.array(mesh.face_areas)[:, 1].sum()
    assert numpy.allclose(face_areas_bottom, base_areas[-1] * len(dz))

    face_areas_section_1 = numpy.array(mesh.face_areas)[:, 2].sum()
    assert numpy.allclose(face_areas_section_1, section_areas)

    face_areas_outer = numpy.array(mesh.face_areas)[:, 3].sum()
    assert numpy.allclose(face_areas_outer, surface_areas.sum())

    face_areas_section_2 = numpy.array(mesh.face_areas)[:, 4].sum()
    assert numpy.allclose(face_areas_section_2, section_areas)

    face_areas_inner = numpy.array(mesh.face_areas)[:, 5].sum()
    assert numpy.allclose(face_areas_inner, surface_areas[:-1].sum())


@pytest.mark.parametrize("ndim", [2, 3])
def test_structured_grid(ndim):
    dx = numpy.array([1.0, 2.0, 3.0, 4.0])
    dy = numpy.array([1.0, 2.0, 3.0])
    dz = numpy.array([1.0, 2.0]) if ndim == 3 else None

    origin = numpy.random.rand(ndim)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=origin)

    assert numpy.allclose(origin, mesh.points.min(axis=0)[:ndim])

    if ndim == 3:
        volumes_ref = dx.sum() * dy.sum() * dz.sum()
        assert numpy.allclose(volumes_ref, mesh.volumes.sum())


@pytest.mark.parametrize("ndim", [2, 3])
def test_triangulate(ndim):
    points = numpy.random.rand(100, ndim)
    mesh = toughio.meshmaker.triangulate(points)

    assert numpy.allclose(points, mesh.points)
    assert mesh.cells[0].type == ("triangle" if ndim == 2 else "tetra")


def test_voxelize():
    dx = numpy.array([1.0, 2.0, 3.0, 4.0])
    dy = numpy.array([1.0, 2.0, 3.0])
    dz = numpy.array([1.0, 2.0])
    origin = numpy.random.rand(3)
    mesh_ref = toughio.meshmaker.structured_grid(dx, dy, dz, origin=origin)

    mesh = toughio.meshmaker.voxelize(mesh_ref.centers, origin=origin)
    helpers.allclose_mesh(mesh_ref, mesh)
