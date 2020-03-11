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


def test_cylindric_mesh():
    """Compare volumes and face areas to analytical values."""
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
