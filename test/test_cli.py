import glob
import os

import numpy
import pytest

import helpers
import toughio


@pytest.mark.parametrize("dirname", [helpers.tempdir(), "abc"])
def test_co2tab(dirname):
    argv = [dirname]

    if os.path.isdir(dirname):
        toughio._cli.co2tab(argv)
        assert os.path.isfile(os.path.join(dirname, "CO2TAB"))
    else:
        with pytest.raises(ValueError):
            toughio._cli.co2tab(argv)


@pytest.mark.parametrize(
    "filename, mesh, ext",
    [
        ("OUTPUT_ELEME.csv", True, "vtu"),
        ("OUTPUT_ELEME.csv", False, "vtu"),
        ("OUTPUT_ELEME.tec", False, "vtu"),
        ("OUTPUT_ELEME.csv", True, "xdmf"),
        ("OUTPUT_ELEME.csv", False, "xdmf"),
        ("OUTPUT_ELEME.tec", False, "xdmf"),
    ],
)
def test_export(filename, mesh, ext):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "tough3", filename)

    outputs = toughio.read_output(filename)

    output_filename = "{}.{}".format(helpers.tempdir(helpers.random_string(10)), ext)
    argv = [
        filename,
        "-o",
        output_filename,
        "-f",
        ext,
    ]

    if mesh:
        argv += [
            "-m",
            os.path.join(this_dir, "support_files", "outputs", "mesh.pickle"),
        ]

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

        centers_ref = numpy.column_stack(
            [outputs[-1].data[dim] for dim in ["X", "Y", "Z"]]
        )
        assert (
            numpy.allclose(
                centers_ref,
                numpy.concatenate([points[c.data].mean(axis=1) for c in cells]),
            )
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


@pytest.mark.parametrize(
    "file_format, split, connection",
    [
        ("csv", True, False),
        ("csv", True, True),
        ("csv", False, False),
        ("csv", False, True),
        ("tecplot", True, False),
        ("tecplot", False, False),
    ],
)
def test_extract(file_format, split, connection):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        this_dir, "support_files", "outputs", "tough3", "OUTPUT.out"
    )
    mesh_file = os.path.join(this_dir, "support_files", "outputs", "MESH.out")

    base_filename = (
        "OUTPUT_ELEME"
        if not connection
        else "OUTPUT_CONNE"
    )

    tempdir = helpers.tempdir()
    output_filename = os.path.join(tempdir, "{}.csv".format(base_filename))

    argv = [
        filename,
        mesh_file,
        "-o",
        output_filename,
        "-f",
        file_format,
    ]
    argv += ["--split"] if split else []
    argv += ["--connection"] if connection else []
    toughio._cli.extract(argv)

    filename_ref = os.path.join(
        this_dir, "support_files", "outputs", "tough3", "{}.csv".format(base_filename)
    )
    outputs_ref = toughio.read_output(filename_ref)

    if not split:
        outputs = toughio.read_output(output_filename, connection=connection)

        for output_ref, output in zip(outputs_ref, outputs):
            assert output_ref.time == output.time
            for k, v in output_ref.data.items():
                assert numpy.allclose(v.mean(), output.data[k].mean(), atol=1.0e-2)
    else:
        filenames = glob.glob(os.path.join(tempdir, "{}_*.csv".format(base_filename)))
        for i, output_filename in enumerate(sorted(filenames)):
            outputs = toughio.read_output(output_filename)

            assert len(outputs) == 1

            output = outputs[0]
            output_ref = outputs_ref[i]

            assert output_ref.time == output.time
            for k, v in output_ref.data.items():
                assert numpy.allclose(v.mean(), output.data[k].mean(), atol=1.0e-2)


@pytest.mark.parametrize("incon", [True, False])
def test_merge(incon):
    tempdir = helpers.tempdir()
    filename = os.path.join(tempdir, "INFILE")
    mesh_file = os.path.join(tempdir, "MESH")
    output_filename = os.path.join(tempdir, "OUTFILE")

    with open(filename, "w") as f:
        n_lines_rocks, n_lines_param = numpy.random.randint(20, size=2) + 1

        f.write("ROCKS\n")
        for _ in range(n_lines_rocks):
            f.write("{}\n".format(helpers.random_string(80)))
        f.write("\n")

        f.write("PARAM\n")
        for _ in range(n_lines_param):
            f.write("{}\n".format(helpers.random_string(80)))

        f.write("ENDCY\n")

    with open(mesh_file, "w") as f:
        n_lines_eleme, n_lines_conne = numpy.random.randint(20, size=2) + 1

        f.write("ELEME\n")
        for _ in range(n_lines_eleme):
            f.write("{}\n".format(helpers.random_string(80)))
        f.write("\n")

        f.write("CONNE\n")
        for _ in range(n_lines_conne):
            f.write("{}\n".format(helpers.random_string(80)))
        f.write("\n")

    if incon:
        incon_file = os.path.join(tempdir, "INCON")

        with open(incon_file, "w") as f:
            n_lines_incon = numpy.random.randint(20) + 1

            f.write("INCON\n")
            for _ in range(n_lines_incon):
                f.write("{}\n".format(helpers.random_string(80)))
            f.write("\n")

    argv = [filename, output_filename]
    toughio._cli.merge(argv)

    with open(output_filename, "r") as f:
        n_lines = 0
        keywords = []
        for line in f:
            n_lines += 1
            if line[:5] in {"ROCKS", "PARAM", "ENDCY", "ELEME", "CONNE", "INCON"}:
                keywords.append(line[:5])

    n_lines_ref = n_lines_rocks + n_lines_param + n_lines_eleme + n_lines_conne
    n_lines_ref += n_lines_incon + 10 if incon else 8
    assert n_lines == n_lines_ref

    assert (
        keywords == ["ROCKS", "PARAM", "ELEME", "CONNE", "ENDCY"]
        if not incon
        else keywords == ["ROCKS", "PARAM", "ELEME", "CONNE", "INCON", "ENDCY"]
    )


@pytest.mark.parametrize("reset", [True, False])
def test_save2incon(reset):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "SAVE.out")
    save = toughio.read_output(filename)

    output_filename = helpers.tempdir(helpers.random_string(10))
    argv = [
        filename,
        output_filename,
    ]

    if reset:
        argv += ["-r"]

    toughio._cli.save2incon(argv)

    incon = toughio.read_output(output_filename)

    assert save.labels.tolist() == incon.labels.tolist()
    helpers.allclose_dict(save.data, incon.data)
