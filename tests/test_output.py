import os

import helpers
import numpy as np
import pytest

import toughio

write_read = lambda output, writer_kws, reader_kws: helpers.write_read(
    "output",
    output,
    toughio.write_output,
    toughio.read_output,
    writer_kws=writer_kws,
    reader_kws=reader_kws,
)


@pytest.mark.parametrize(
    "filename, filename_ref",
    [
        ("OUTPUT_ELEME.csv", "SAVE.out"),
        ("OUTPUT_ELEME.tec", "SAVE.out"),
        ("OUTPUT_ELEME_PETRASIM.csv", "SAVE.out"),
        ("OUTPUT.out", "SAVE.out"),
        ("OUTPUT_6.out", "SAVE_6.out"),
    ],
)
def test_output_eleme(filename, filename_ref):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", filename)
    outputs = toughio.read_output(filename)

    filename = os.path.join(this_dir, "support_files", "outputs", filename_ref)
    save = toughio.read_output(filename)

    assert len(outputs) == 5

    times_ref = [
        0.2592000e08,
        0.3155800e08,
        0.1577900e09,
        0.3155800e09,
        0.7889400e09,
    ]
    keys_ref = ["POR", "PRES", "SAT_G", "TEMP", "X", "Y", "Z"]
    for output, time_ref in zip(outputs, times_ref):
        assert time_ref == output.time
        assert (
            save.labels.tolist() == output.labels.tolist()
            if output.format in {"csv", "petrasim", "tough"}
            else len(output.labels) == 0
        )
        if output.format != "tough":
            assert keys_ref == sorted(list(output.data))

    assert helpers.allclose(save.data["X1"], outputs[-1].data["PRES"])
    assert helpers.allclose(save.data["X2"], outputs[-1].data["TEMP"], atol=0.1)


@pytest.mark.parametrize(
    "filename",
    ["OUTPUT_CONNE.csv", "OUTPUT.out", "OUTPUT_6.out"],
)
def test_output_conne(filename):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", filename)
    outputs = toughio.read_output(filename, connection=True)

    times_ref = [
        0.2592000e08,
        0.3155800e08,
        0.1577900e09,
        0.3155800e09,
        0.7889400e09,
    ]
    data_ref = [
        52542.0,
        52475.0,
        51146.0,
        49600.0,
        45623.0,
    ]
    for output, time_ref, data in zip(outputs, times_ref, data_ref):
        assert time_ref == output.time
        assert (
            len(set("".join(labels) for labels in output.labels))
            == output.data["HEAT"].size
        )
        assert helpers.allclose(data, np.abs(output.data["HEAT"]).mean(), atol=1.0)


@pytest.mark.parametrize(
    "output_ref, file_format",
    [
        (helpers.output_eleme, "csv"),
        (helpers.output_eleme[0], "csv"),
        (helpers.output_eleme, "petrasim"),
        (helpers.output_eleme[0], "petrasim"),
        (helpers.output_eleme, "tecplot"),
        (helpers.output_eleme[0], "tecplot"),
        (helpers.output_conne, "csv"),
        (helpers.output_conne[0], "csv"),
    ],
)
def test_output(output_ref, file_format):
    output = write_read(
        output=output_ref,
        writer_kws={"file_format": file_format},
        reader_kws={},
    )

    output_ref = output_ref if isinstance(output_ref, list) else [output_ref]
    for out_ref, out in zip(output_ref, output):
        # Careful here, tecplot format has no label
        helpers.allclose(out, out_ref)


def test_save():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "SAVE.out")
    save = toughio.read_output(filename)

    x_ref = [6.35804123e05, 1.42894499e02, 9.91868799e-01]
    assert helpers.allclose(
        x_ref, np.mean([save.data["X1"], save.data["X2"], save.data["X3"]], axis=1)
    )

    assert helpers.allclose(0.01, save.data["porosity"].mean())

    assert "userx" not in save.data
