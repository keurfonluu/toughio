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

    volumes = mesh.volumes.sum()
    assert helpers.allclose(volumes, base_areas[-1] * dz.sum())

    # Interface areas of internal connections
    connections = mesh.to_tough()["connections"].values()
    isot = np.array([v["permeability_direction"] for v in connections])
    areas = np.array([v["interface_area"] for v in connections])

    # Horizontal faces between layers: one full disk per internal interface
    face_areas_horizontal = areas[isot == 3].sum()
    assert helpers.allclose(face_areas_horizontal, base_areas[-1] * (len(dz) - 1))

    # Vertical faces between rings: lateral surface of each internal radius
    face_areas_vertical = areas[isot == 1].sum()
    assert helpers.allclose(face_areas_vertical, surface_areas[:-1].sum())


@pytest.mark.parametrize("ndim", [2, 3])
def test_structured_grid(ndim):
    dx = np.array([1.0, 2.0, 3.0, 4.0])
    dy = np.array([1.0, 2.0, 3.0])
    dz = np.array([1.0, 2.0]) if ndim == 3 else None

    origin = np.random.rand(ndim)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=origin)

    assert helpers.allclose(origin, mesh.points.min(axis=0)[:ndim])

    if ndim == 2:
        assert np.allclose(mesh.points[:, 2], 0.0)

    if ndim == 3:
        volumes_ref = dx.sum() * dy.sum() * dz.sum()
        assert helpers.allclose(volumes_ref, mesh.volumes.sum())


@pytest.mark.parametrize("ndim", [2, 3])
def test_triangulate(ndim):
    points = np.random.rand(100, ndim)
    mesh = toughio.meshmaker.triangulate(points)

    assert helpers.allclose(points, mesh.points[:, :ndim])
    assert mesh.to_meshio().cells[0].type == ("triangle" if ndim == 2 else "tetra")
    assert (mesh.materials == "dfalt").all()


def test_voxelize():
    dx = np.array([1.0, 2.0, 3.0, 4.0])
    dy = np.array([1.0, 2.0, 3.0])
    dz = np.array([1.0, 2.0])
    origin = np.random.rand(3)
    mesh_ref = toughio.meshmaker.structured_grid(dx, dy, dz, origin=origin)

    mesh = toughio.meshmaker.voxelize(mesh_ref.centers, origin=origin)
    helpers.allclose(mesh_ref, mesh)


def test_layer():
    dr = np.array([1.0, 2.0, 3.0, 4.0])
    dz = np.array([1.0, 2.0, 3.0])

    mesh = toughio.meshmaker.cylindric_grid(dr, dz, layer=False)
    mesh_layer = toughio.meshmaker.cylindric_grid(dr, dz, layer=True)

    point = 3.5, 0.0, -1.5
    i1 = mesh.find_nearest_cell(point)
    i2 = mesh_layer.find_nearest_cell(point)

    assert helpers.allclose(mesh.volumes[i1], mesh_layer.volumes[i2])
    assert helpers.allclose(
        _connection_areas(mesh, i1), _connection_areas(mesh_layer, i2)
    )


def test_from_meshmaker_xyz():
    parameters = {
        "meshmaker": {
            "type": "xyz",
            "parameters": [
                {"type": "nx", "n_increment": 3, "sizes": 14.09},
                {"type": "ny", "n_increment": 10, "sizes": np.arange(10) + 1.0},
                {"type": "nz", "n_increment": 3, "sizes": [14.0, 0.9, 19.91]},
            ],
        }
    }
    mesh = toughio.meshmaker.from_meshmaker(parameters)

    assert mesh.n_cells == 90
    assert helpers.allclose(mesh.points[:, 0].max(), 3 * 14.09)
    assert helpers.allclose(mesh.points[:, 1].max(), 55.0)
    assert helpers.allclose(mesh.points[:, 2].min(), -14.0 - 0.9 - 19.91)


def test_from_meshmaker_rz2d():
    parameters = {
        "meshmaker": {
            "type": "rz2d",
            "parameters": [
                {"type": "radii", "radii": np.arange(10)},
                {"type": "equid", "n_increment": 3, "size": 14.09},
                {
                    "type": "logar",
                    "n_increment": 14,
                    "radius": 64.0,
                    "radius_ref": 0.9,
                },
                {"type": "layer", "thicknesses": [14.0, 0.9, 19.91]},
            ],
        }
    }
    mesh = toughio.meshmaker.from_meshmaker(parameters)

    assert mesh.n_cells == 26 * 3
    assert helpers.allclose(mesh.points[:, 0].max(), 64.0)
    assert helpers.allclose(mesh.points[:, 2].min(), -14.0 - 0.9 - 19.91)
    assert helpers.allclose(np.ptp(mesh.points[:, 0]), 64.0)
    assert helpers.allclose(np.ptp(mesh.points[:, 2]), 14 + 0.9 + 19.91)


def _connection_areas(mesh, i):
    """Sorted interface areas of all connections of cell *i*."""
    label = mesh.labels[i]
    connections = mesh.to_tough()["connections"]
    n = len(label)

    return sorted(
        v["interface_area"] for k, v in connections.items() if label in {k[:n], k[n:]}
    )
