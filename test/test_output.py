import os

import numpy
import pytest

import toughio


@pytest.mark.parametrize(
    "filename, file_format",
    [("OUTPUT_ELEME.csv", "tough"), ("OUTPUT_ELEME.tec", "tecplot")],
)
def test_output(filename, file_format):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "tough3", filename)
    outputs = toughio.read_output(filename, file_format=file_format)

    filename = os.path.join(this_dir, "support_files", "outputs", "SAVE.out")
    save = toughio.read_save(filename)

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
            if file_format == "tough"
            else output.labels == None
        )
        assert keys_ref == sorted(list(output.data.keys()))

    assert numpy.allclose(save.data["X1"], outputs[-1].data["PRES"])
    assert numpy.allclose(save.data["X2"], outputs[-1].data["TEMP"])


def test_save():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "SAVE.out")
    save = toughio.read_save(filename)

    x_ref = [6.35804123e05, 1.42894499e02, 9.91868799e-01]
    assert numpy.allclose(x_ref, numpy.mean([v for v in save.data.values()], axis=1))
