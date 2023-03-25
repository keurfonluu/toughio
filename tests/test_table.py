import os

import helpers
import pytest

import toughio


@pytest.mark.parametrize(
    "filename, file_format, data_ref",
    [
        (
            "FOFT_A1912.csv",
            "csv",
            {
                "TIME(S)": 4.393722000e9,
                "PRES": 1.8740899675005e8,
                "TEMP": 720.0,
                "SAT_G": 0.0,
                "SAT_L": 24.0,
            },
        ),
        (
            "FOFT_A1912_T2.csv",
            "csv",
            {
                "TIME(S)": 3.06639400e9,
                "PRES": 1.83000721e8,
                "TEMP": 660.0,
                "SAT_G": 0.0,
                "SAT_L": 22.0,
            },
        ),
        (
            "FOFT_A1912.col",
            "column",
            {
                "TIME [s]": 4.393722000e9,
                "1 PRES": 1.8740899675005e8,
                "2 TEMP": 720.0,
                "3 SAT_G": 0.0,
                "4 SAT_L": 24.0,
            },
        ),
        (
            "FOFT_A1912.tec",
            "tecplot",
            {
                "Time [s]": 4.393722000e9,
                "1 PRES": 1.8740899675005e8,
                "2 TEMP": 720.0,
                "3 SAT_G": 0.0,
                "4 SAT_L": 24.0,
            },
        ),
        (
            "FOFT_A1912.foft",
            "csv",
            {
                "TIME [s]": 4.393722000e9,
                "PRES": 1.8740899675005e8,
                "TEMP": 720.0,
                "SAT_G": 0.0,
                "SAT_L": 24.0,
            },
        ),
        (
            "GOFT_A1162.csv",
            "csv",
            {
                "TIME(S)": 4.393722000e9,
                "GEN": -30.0,
                "ENTG": 1.528048035348e7,
                "PWB": 0.0,
            },
        ),
        (
            "GOFT_A1162_T2.csv",
            "csv",
            {"TIME(S)": 3.06639400e9, "GEN": -27.5, "ENTG": 1.40141971e7, "PWB": 0.0},
        ),
    ],
)
def test_table(filename, file_format, data_ref):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "outputs", filename)
    data = toughio.read_table(filename, file_format=file_format)

    for k, v in data_ref.items():
        assert helpers.allclose(v, data[k].sum())
