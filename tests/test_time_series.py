import helpers
import numpy as np

import toughio


def test_time_series():
    # Import hybrid mesh
    mesh_ref = helpers.hybrid_mesh.copy()

    # Create random time series
    num_steps = 5
    cell_data_ref = [
        {"cells": np.random.rand(mesh_ref.n_cells)} for _ in range(num_steps)
    ]
    time_steps_ref = np.sort(np.random.rand(num_steps))

    # Write and read back XDMF
    filepath = helpers.tempdir("test.xdmf")
    toughio.write_time_series(filepath, mesh_ref, cell_data_ref, time_steps_ref)
    mesh, cell_data, time_steps = toughio.read_time_series(filepath)

    # Compare with reference data
    assert helpers.allclose(mesh.points, mesh_ref.points)

    for cell_ref, cell in zip(mesh_ref.to_meshio().cells, mesh.to_meshio().cells):
        assert cell_ref.type == cell.type
        assert helpers.allclose(cell_ref.data, cell.data)

    assert len(cell_data) == num_steps
    for cdata, cdata_ref in zip(cell_data, cell_data_ref):
        assert helpers.allclose(cdata["cells"], cdata_ref["cells"])

    assert helpers.allclose(time_steps, time_steps_ref)
