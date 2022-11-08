import os
import sys
from copy import deepcopy

import helpers
import numpy as np
import pytest

import toughio

output_ref = {
    "element": {
        0: {
            "PRES": 9641264.130638,
            "TEMP": 149.62999493,
        },
        -1: {
            "PRES": 635804.12294844,
            "TEMP": 142.89449866,
        },
    },
    "connection": {
        0: {
            "HEAT": -1.64908253e-07,
            "FLOW": -2.85760551e-13,
        },
        -1: {
            "HEAT": -5.54750914e-08,
            "FLOW": -4.68234504e-14,
        },
    },
}


def test_print():
    print(helpers.hex_mesh)


def test_extrude_to_3d():
    # Create 2D mesh
    dx = np.random.rand(10)
    dy = np.random.rand(5)
    mesh_ref = toughio.meshmaker.structured_grid(dx, dy)
    mesh_ref.point_data["a"] = np.random.rand(mesh_ref.n_points)
    mesh_ref.point_data["b"] = np.random.rand(mesh_ref.n_points, 3)
    mesh_ref.cell_data["c"] = np.random.rand(mesh_ref.n_cells)
    mesh_ref.cell_data["d"] = np.random.rand(mesh_ref.n_cells, 3)

    # Extrude mesh to 3D
    mesh = mesh_ref.extrude_to_3d(np.random.rand(5), axis=2, inplace=False)

    assert mesh.n_points == 6 * mesh_ref.n_points
    assert mesh.n_cells == 5 * mesh_ref.n_cells
    assert mesh.point_data["a"].shape == (6 * mesh_ref.n_points,)
    assert mesh.point_data["b"].shape == (6 * mesh_ref.n_points, 3)
    assert mesh.cell_data["c"].shape == (5 * mesh_ref.n_cells,)
    assert mesh.cell_data["d"].shape == (5 * mesh_ref.n_cells, 3)

    for v in mesh.point_data["a"].reshape((6, mesh.n_points // 6)):
        assert helpers.allclose(mesh_ref.point_data["a"], v)

    for v in mesh.point_data["b"].reshape((6, mesh.n_points // 6, 3)):
        assert helpers.allclose(mesh_ref.point_data["b"], v)

    for v in mesh.cell_data["c"].reshape((5, mesh.n_cells // 5)):
        assert helpers.allclose(mesh_ref.cell_data["c"], v)

    for v in mesh.cell_data["d"].reshape((5, mesh.n_cells // 5, 3)):
        assert helpers.allclose(mesh_ref.cell_data["d"], v)


def test_prune_duplicates():
    # Create mesh with duplicate points and cells
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
            [2.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [2.0, 0.0, 1.0],
            [2.0, 1.0, 1.0],
            [2.5, 0.5, 0.5],
            [2.5, 0.5, 0.5],
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    )
    cells = [
        ("tetra", np.array([[8, 12, 9, 10], [10, 13, 9, 11]])),
        (
            "wedge",
            np.array(
                [[1, 10, 5, 2, 11, 6], [1, 10, 5, 2, 11, 6], [1, 8, 10, 2, 9, 11]]
            ),
        ),
        (
            "hexahedron",
            np.array([[0, 1, 2, 3, 4, 5, 6, 7], [14, 15, 16, 17, 18, 19, 20, 21]]),
        ),
    ]
    mesh = toughio.Mesh(points, cells)
    mesh.point_data["points"] = np.random.rand(mesh.n_points)
    mesh.cell_data["cells"] = np.random.rand(mesh.n_cells)

    # Remove duplicate points and cells
    mesh.prune_duplicates()

    assert mesh.n_points == 13
    assert mesh.n_cells == 5
    assert mesh.point_data["points"].size == 13
    assert mesh.cell_data["cells"].size == 5


@pytest.mark.parametrize(
    "mesh_ref, from_, to_",
    [
        (helpers.tet_mesh, toughio.from_meshio, "to_meshio"),
        (helpers.tet_mesh, toughio.from_pyvista, "to_pyvista"),
        (helpers.hex_mesh, toughio.from_meshio, "to_meshio"),
        (helpers.hex_mesh, toughio.from_pyvista, "to_pyvista"),
    ],
)
def test_from_to(mesh_ref, from_, to_):
    mesh = from_(getattr(mesh_ref, to_)())

    helpers.allclose(mesh_ref, mesh)


@pytest.mark.parametrize(
    "filename, file_type, time_step",
    [
        ("OUTPUT_ELEME.csv", "element", 0),
        ("OUTPUT_ELEME.csv", "element", -1),
        ("OUTPUT_CONNE.csv", "connection", 0),
        ("OUTPUT_CONNE.csv", "connection", -1),
    ],
)
def test_read_output(filename, file_type, time_step):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    mesh_filename = os.path.join(this_dir, "support_files", "outputs", "mesh.pickle")
    mesh = toughio.read_mesh(mesh_filename)
    filename = os.path.join(this_dir, "support_files", "outputs", filename)

    outputs = toughio.read_output(filename)
    helpers.convert_outputs_labels(outputs, file_type == "connection")
    mesh.read_output(outputs, time_step=time_step)
    # mesh.read_output(filename, time_step=time_step)

    for k, v in output_ref[file_type][time_step].items():
        assert helpers.allclose(v, mesh.cell_data[k].mean())


def test_add_material():
    mesh = deepcopy(helpers.hybrid_mesh)
    mesh.add_material("a", 1)

    assert helpers.allclose(mesh.materials, np.array(["a"] * mesh.n_cells))


def test_add_point_data():
    mesh = deepcopy(helpers.hybrid_mesh)
    data = np.random.rand(mesh.n_points)
    mesh.add_point_data("a", data)

    assert helpers.allclose(data, mesh.point_data["a"])


def test_add_cell_data():
    mesh = deepcopy(helpers.hybrid_mesh)
    data = np.random.rand(mesh.n_cells)
    mesh.add_cell_data("a", data)

    assert helpers.allclose(data, mesh.cell_data["a"])


@pytest.mark.parametrize("bool_cells", [False, True])
def test_set_material(bool_cells):
    dx = np.ones(10)
    dy = np.ones(10)
    dz = np.ones(10)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=np.zeros(3))

    idx = mesh.filter.box(4.0, 4.0, 4.0, 2.0, 2.0, 2.0)
    if bool_cells:
        cells = np.zeros(mesh.n_cells, dtype=bool)
        cells[idx] = True
    else:
        cells = idx
    mesh.set_material("test", cells)

    assert (mesh.materials == "test").sum() == 8


def test_set_cell_labels():
    mesh = deepcopy(helpers.hybrid_mesh)
    labels = [helpers.random_label(5) for _ in range(mesh.n_cells)]
    mesh.set_cell_labels(labels)

    for label, label_ref in zip(mesh.labels, labels):
        assert label == label_ref


def test_cell_data_to_point_data():
    mesh = deepcopy(helpers.hybrid_mesh)
    data = np.ones(mesh.n_cells)
    mesh.add_cell_data("a", data)
    mesh.cell_data_to_point_data()

    assert helpers.allclose(np.ones(mesh.n_points), mesh.point_data["a"])
    assert "a" not in mesh.cell_data


def test_point_data_to_cell_data():
    mesh = deepcopy(helpers.hybrid_mesh)
    data = np.ones(mesh.n_points)
    mesh.add_point_data("a", data)
    mesh.point_data_to_cell_data()

    assert helpers.allclose(np.ones(mesh.n_cells), mesh.cell_data["a"])
    assert "a" not in mesh.point_data


def test_near():
    dx = np.ones(3)
    dy = np.ones(3)
    dz = np.ones(3)
    mesh = toughio.meshmaker.structured_grid(dx, dy, dz, origin=np.zeros(3))

    assert mesh.near((1.5, 1.5, 1.5)) == 13


@pytest.mark.skipif(sys.version_info < (3, 6), reason="Order of keys in dictionary")
@pytest.mark.parametrize(
    "num_pvars, eos",
    [(4, None), (6, None), (4, "tmvoc")],
)
def test_write_tough(num_pvars, eos):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "all_cell_types.f3grid")
    mesh_ref = toughio.read_mesh(filename)

    tempdir = helpers.tempdir()
    mesh_filename = os.path.join(tempdir, "MESH")
    incon_filename = os.path.join(tempdir, "INCON")

    pvars = np.random.rand(mesh_ref.n_cells, num_pvars)
    mesh_ref.add_cell_data("initial_condition", pvars)

    bcond = (mesh_ref.centers[:, 2] < 0.5).astype(int)
    mesh_ref.add_cell_data("boundary_condition", bcond)

    if eos == "tmvoc":
        indicat0 = np.random.randint(10, size=mesh_ref.n_cells)
        mesh_ref.add_cell_data("phase_composition", indicat0)

    mesh_ref.write_tough(mesh_filename, incon=True, eos=eos)
    mesh = toughio.read_input(mesh_filename, file_format="tough", eos=eos)
    incon = toughio.read_input(incon_filename, file_format="tough", eos=eos)

    volumes = [v["volume"] for v in mesh["elements"].values()]
    volumes = [v if v < 1.0e20 else v * 1.0e-50 for v in volumes]
    assert helpers.allclose(mesh_ref.volumes, volumes, atol=1.0e-6)

    centers = [v["center"] for v in mesh["elements"].values()]
    assert helpers.allclose(mesh_ref.centers, centers, atol=1.0e-3)

    pvars = np.row_stack([v["values"] for v in incon["initial_conditions"].values()])
    assert helpers.allclose(mesh_ref.cell_data["initial_condition"], pvars)

    if eos == "tmvoc":
        indicat0 = [
            v["phase_composition"] for v in incon["initial_conditions"].values()
        ]
        assert helpers.allclose(mesh_ref.cell_data["phase_composition"], indicat0)
