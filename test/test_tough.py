import numpy
import pytest

import helpers
import toughio


@pytest.mark.parametrize(
    "nodal_distance, bound",
    [("line", True), ("line", False), ("orthogonal", True), ("orthogonal", False)],
)
def test_mesh(nodal_distance, bound):
    # Create 3D mesh
    dx = numpy.arange(3) + 1
    dy = numpy.arange(4) + 1
    dz = numpy.arange(5) + 1
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, material=helpers.random_string(5))

    idx = numpy.random.choice(mesh.n_cells, mesh.n_cells // 2, replace=False)
    mesh.cell_data["material"][idx] = 2
    mesh.field_data[helpers.random_string(5)] = numpy.array([2, 3])

    idx = numpy.random.choice(mesh.n_cells, mesh.n_cells // 2, replace=False)
    boundary_condition = (
        (numpy.random.rand(mesh.n_cells) < numpy.random.rand()).astype(int)
        if bound
        else numpy.zeros(mesh.n_cells)
    )
    mesh.add_cell_data("boundary_condition", boundary_condition)

    parameters = helpers.write_read(
        filename="MESH",
        obj=mesh,
        writer=toughio.write_mesh,
        reader=toughio.read_mesh,
        writer_kws={"file_format": "tough", "nodal_distance": nodal_distance},
        reader_kws={"file_format": "tough"},
    )

    # Check block ELEME
    assert sorted(mesh.labels) == sorted(parameters["elements"].keys())

    materials = [parameters["elements"][label]["material"] for label in mesh.labels]
    assert mesh.materials.tolist() == materials

    volumes = [parameters["elements"][label]["volume"] for label, bcond in zip(mesh.labels, boundary_condition) if not bcond]
    assert numpy.allclose(mesh.volumes[boundary_condition == 0], volumes)

    volumes = [parameters["elements"][label]["volume"] for label, bcond in zip(mesh.labels, boundary_condition) if bcond]
    assert numpy.allclose(mesh.volumes[boundary_condition == 1] * 1.0e50, volumes)

    centers = [parameters["elements"][label]["center"] for label in mesh.labels]
    assert numpy.allclose(mesh.centers, centers)

    # Check block CONNE
    nx, ny, nz = len(dx), len(dy), len(dz)
    lx, ly, lz = sum(dx), sum(dy), sum(dz)

    isot_x = [v["permeability_direction"] == 1 for v in parameters["connections"].values()]
    assert sum(isot_x) == (nx - 1) * ny * nz

    isot_y = [v["permeability_direction"] == 2 for v in parameters["connections"].values()]
    assert sum(isot_y) == nx * (ny - 1) * nz

    isot_z = [v["permeability_direction"] == 3 for v in parameters["connections"].values()]
    assert sum(isot_z) == nx * ny * (nz - 1)

    interface_areas = [v["interface_area"] for v in parameters["connections"].values()]
    assert sum(interface_areas) == (nx - 1) * ly * lz + (ny - 1) * lx * lz + (nz - 1) * lx * ly

    angles = [v["gravity_cosine_angle"] == 0.0 for v in parameters["connections"].values()]
    assert sum(angles) == sum(isot_x) + sum(isot_y)

    angles = [v["gravity_cosine_angle"] == -1.0 for v in parameters["connections"].values()]
    assert sum(angles) == sum(isot_z)

    if not bound:
        xmin, ymin, zmin = mesh.centers.min(axis=0)
        xmax, ymax, zmax = mesh.centers.max(axis=0)
        distances_ref = ny * nz * (xmax - xmin) + nx * nz * (ymax - ymin) + nx * ny * (zmax - zmin)
        distances = [v["nodal_distances"] for v in parameters["connections"].values()]
        assert numpy.allclose(distances_ref, numpy.sum(distances))
