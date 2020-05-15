import os

import numpy
import pytest

import toughio


@pytest.mark.parametrize(
    "filename, data_ref",
    [
        (
            "FOFT_A1912.csv",
            {
                "TIME": 3.06639400e9,
                "PRES": 1.83000721e8,
                "TEMP": 660.0,
                "SAT_G": 0.0,
                "SAT_L": 22.0,
            },
        ),
        (
            "GOFT_A1162.csv",
            {"TIME": 3.06639400e9, "GEN": -27.5, "ENTG": 1.40141971e7, "PWB": 0.0},
        ),
    ],
)
def test_history(filename, data_ref):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", filename)
    data = toughio.read_history(filename)

    for k, v in data_ref.items():
        assert numpy.allclose(v, data[k].sum())


@pytest.mark.parametrize("filename", ["OUTPUT_ELEME.csv", "OUTPUT_ELEME.tec"])
def test_output(filename):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", "tough3", filename)
    outputs = toughio.read_output(filename)

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
            if output.format == "tough"
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
    assert numpy.allclose(
        x_ref, numpy.mean([save.data["X1"], save.data["X2"], save.data["X3"]], axis=1)
    )

    assert numpy.allclose(0.01, save.data["porosity"].mean())

    assert "userx" not in save.data.keys()
