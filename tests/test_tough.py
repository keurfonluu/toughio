import os

import helpers
import numpy as np
import pytest

import toughio


@pytest.mark.parametrize(
    "assume_orthogonal, bound",
    [
        (False, True),
        (False, False),
        (True, True),
        (True, False),
    ],
)
def test_mesh(assume_orthogonal, bound):
    # Create 3D mesh
    dx = np.arange(3) + 1
    dy = np.arange(4) + 1
    dz = np.arange(5) + 1
    mesh = toughio.meshmaker.structured_grid(
        dx, dy, dz, material=helpers.random_string(5)
    )

    idx = np.random.choice(mesh.n_cells, mesh.n_cells // 2, replace=False)
    mesh.set_material(helpers.random_string(5), idx)

    boundary_condition = (
        (np.random.rand(mesh.n_cells) < np.random.rand()).astype(int)
        if bound
        else np.zeros(mesh.n_cells, dtype=int)
    )
    mesh.dirichlet = boundary_condition

    parameters = helpers.write_read(
        filename="MESH",
        obj=None,
        writer=mesh.write_tough,
        reader=toughio.read_mesh,
        writer_kws={"assume_orthogonal": assume_orthogonal},
        reader_kws={"file_format": "tough"},
    )

    # Check block ELEME
    assert sorted(mesh.labels) == sorted(parameters["elements"])

    materials = [parameters["elements"][label]["material"] for label in mesh.labels]
    assert mesh.materials.tolist() == materials

    volumes = [
        parameters["elements"][label]["volume"]
        for label, bcond in zip(mesh.labels, boundary_condition)
        if not bcond
    ]
    assert helpers.allclose(mesh.volumes[boundary_condition == 0], volumes)

    volumes = [
        parameters["elements"][label]["volume"]
        for label, bcond in zip(mesh.labels, boundary_condition)
        if bcond
    ]
    assert helpers.allclose(np.full(boundary_condition.sum(), 1.0e50), volumes)

    centers = [parameters["elements"][label]["center"] for label in mesh.labels]
    assert helpers.allclose(mesh.centers, centers)

    # Check block CONNE
    nx, ny, nz = len(dx), len(dy), len(dz)
    lx, ly, lz = sum(dx), sum(dy), sum(dz)

    isot_x = [
        v["permeability_direction"] == 1 for v in parameters["connections"].values()
    ]
    assert sum(isot_x) == (nx - 1) * ny * nz

    isot_y = [
        v["permeability_direction"] == 2 for v in parameters["connections"].values()
    ]
    assert sum(isot_y) == nx * (ny - 1) * nz

    isot_z = [
        v["permeability_direction"] == 3 for v in parameters["connections"].values()
    ]
    assert sum(isot_z) == nx * ny * (nz - 1)

    interface_areas = [v["interface_area"] for v in parameters["connections"].values()]
    assert (
        sum(interface_areas)
        == (nx - 1) * ly * lz + (ny - 1) * lx * lz + (nz - 1) * lx * ly
    )

    angles = [
        v["gravity_cosine_angle"] == 0.0 for v in parameters["connections"].values()
    ]
    assert sum(angles) == sum(isot_x) + sum(isot_y)

    angles = [
        v["gravity_cosine_angle"] == 1.0 for v in parameters["connections"].values()
    ]
    assert sum(angles) == sum(isot_z)

    if not bound:
        xmin, ymin, zmin = mesh.centers.min(axis=0)
        xmax, ymax, zmax = mesh.centers.max(axis=0)
        distances_ref = (
            ny * nz * (xmax - xmin) + nx * nz * (ymax - ymin) + nx * ny * (zmax - zmin)
        )
        distances = [v["nodal_distances"] for v in parameters["connections"].values()]
        assert helpers.allclose(distances_ref, np.sum(distances))


@pytest.mark.parametrize("anisotropic", [True, False, None])
def test_incon(anisotropic):
    # Create 3D mesh
    dx = np.arange(3) + 1
    dy = np.arange(4) + 1
    dz = np.arange(5) + 1
    mesh = toughio.meshmaker.structured_grid(
        dx, dy, dz, material=helpers.random_string(5)
    )

    initial_condition = np.random.rand(mesh.n_cells, 4)
    mesh.initial_conditions = initial_condition

    porosity = np.random.rand(mesh.n_cells)
    mesh.porosities = porosity

    if anisotropic is not None:
        permeability = (
            np.random.rand(mesh.n_cells, 3)
            if anisotropic
            else np.random.rand(mesh.n_cells)
        )
        mesh.permeabilities = permeability

    # INCON is written next to MESH when incon=True
    filename = helpers.tempdir("MESH")
    mesh.write_tough(filename, incon=True)
    parameters = toughio.read_mesh(
        os.path.join(os.path.dirname(filename), "INCON"), file_format="tough"
    )

    # Check block INCON
    assert sorted(mesh.labels) == sorted(parameters["initial_conditions"])

    values = [
        parameters["initial_conditions"][label]["values"] for label in mesh.labels
    ]
    assert helpers.allclose(initial_condition, values)

    porosity = [
        parameters["initial_conditions"][label]["porosity"] for label in mesh.labels
    ]
    assert helpers.allclose(mesh.porosities, porosity)

    if anisotropic is not None:
        userx = np.array(
            [parameters["initial_conditions"][label]["userx"] for label in mesh.labels]
        )
        permeability = userx[:, :3] if anisotropic else userx[:, 0]
        assert helpers.allclose(mesh.permeabilities, permeability, atol=1.0e-4)
