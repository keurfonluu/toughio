import os
import tempfile
from copy import deepcopy

import meshio
import numpy

import helpers
import toughio


def test_time_series():
    # Import hybrid mesh
    mesh = deepcopy(helpers.hybrid_mesh)

    # Create random time series
    num_steps = 5
    point_data_ref = [
        {"points": numpy.random.rand(mesh.n_points)} for _ in range(num_steps)
    ]
    cell_data_ref = [
        {"cells": mesh.split(numpy.random.rand(mesh.n_cells))} for i in range(num_steps)
    ]
    time_steps_ref = numpy.sort(numpy.random.rand(num_steps))

    # Write and read back XDMF
    temp_dir = tempfile.mkdtemp().replace("\\", "/")
    filepath = os.path.join(temp_dir, "test.xdmf")
    toughio.write_time_series(
        filepath,
        mesh.points,
        mesh.cells,
        point_data_ref,
        cell_data_ref,
        time_steps_ref,
    )
    out = toughio.read_time_series(filepath)
    points, cells, point_data, cell_data, time_steps = out

    # Compare with reference data
    assert numpy.allclose(points, mesh.points)

    for cell_ref, cell in zip(mesh.cells, cells):
        assert cell_ref.type == cell.type
        assert numpy.allclose(cell_ref.data, cell.data)

    for t, pdata in enumerate(point_data):
        for k, v in pdata.items():
            assert numpy.allclose(v, point_data_ref[t][k])

    for t, cdata in enumerate(cell_data):
        for k, v in cdata.items():
            assert numpy.allclose(
                numpy.concatenate(v), numpy.concatenate(cell_data_ref[t][k])
            )

    assert numpy.allclose(time_steps, time_steps_ref)
