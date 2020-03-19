import os

import numpy
import pytest

import helpers
import toughio


@pytest.mark.parametrize(
    "filename, file_format, mesh, ext",
    [
        ("OUTPUT_ELEME.csv", "tough", True, "vtu"),
        ("OUTPUT_ELEME.csv", "tough", False, "vtu"),
        ("OUTPUT_ELEME.tec", "tecplot", False, "vtu"),
        ("OUTPUT_ELEME.csv", "tough", True, "xdmf"),
        ("OUTPUT_ELEME.csv", "tough", False, "xdmf"),
        ("OUTPUT_ELEME.tec", "tecplot", False, "xdmf"),
    ],
)
def test_export(filename, file_format, mesh, ext):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "tough3", filename)

    outputs = toughio.read_output(filename, file_format=file_format)

    output_filename = "{}.{}".format(helpers.tempdir(helpers.random_string(10)), ext)
    argv = [
        filename,
        "-i", file_format,
        "-o", output_filename,
        "-f", ext,
    ]

    if mesh:
        argv += ["-m", os.path.join(this_dir, "support_files", "outputs", "mesh.pickle")]

    if ext != "xdmf":
        t = numpy.random.randint(len(outputs))
        argv += ["-t", str(t)]
        output = outputs[t]
    
    toughio._cli.export(argv)

    if ext != "xdmf":
        mesh_in = toughio.read_mesh(output_filename)

        centers_ref = numpy.column_stack([output.data[dim] for dim in ["X", "Y", "Z"]])
        assert (
            numpy.allclose(centers_ref, mesh_in.centers)
            if mesh
            else numpy.allclose(centers_ref[:, :2], mesh_in.points[:, :2])
        )

        for k, v in output.data.items():
            if k not in {"X", "Y", "Z"}:
                assert (
                    numpy.allclose(v, mesh_in.cell_data[k])
                    if mesh
                    else numpy.allclose(v, mesh_in.point_data[k])
                )
    else:
        mesh_in = toughio.read_time_series(output_filename)
        points, cells, point_data, cell_data, time_steps = mesh_in

        centers_ref = numpy.column_stack([outputs[-1].data[dim] for dim in ["X", "Y", "Z"]])
        assert (
            numpy.allclose(centers_ref, numpy.concatenate([points[c.data].mean(axis=1) for c in cells]))
            if mesh
            else numpy.allclose(centers_ref[:, :2], points[:, :2])
        )

        assert len(point_data) == len(outputs)
        assert len(cell_data) == len(outputs)

        assert (
            all(pdata == {} for pdata in point_data)
            if mesh
            else all(cdata == {} for cdata in cell_data)
        )

        for t, pdata in enumerate(point_data):
            for k, v in pdata.items():
                assert numpy.allclose(v, outputs[t].data[k])

        for t, cdata in enumerate(cell_data):
            for k, v in cdata.items():
                assert numpy.allclose(v, outputs[t].data[k])

        time_steps_ref = [output.time for output in outputs]
        assert numpy.allclose(time_steps, time_steps_ref)
