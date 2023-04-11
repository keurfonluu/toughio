import h5py
import helpers
import pathlib

import toughio


def test_h5():
    this_dir = pathlib.Path(__file__).parent
    path = this_dir / "support_files" / "outputs"
    filename = helpers.tempdir("output.h5")

    toughio.write_h5(
        filename=filename,
        elements=path / "OUTPUT_ELEME.csv",
        connections=path / "OUTPUT_CONNE.csv",
        element_history={"A1912": path / "FOFT_A1912.csv"},
        connection_history={"A1912": path / "FOFT_A1912.csv"},
        generator_history={"A1162": path / "GOFT_A1162.csv"},
        rock_history={"ROCK": path / "ROFT.csv"},
    )

    with h5py.File(filename, "r") as f:
        assert list(f.keys()) == ["connection_history", "connections", "element_history", "elements", "generator_history", "rock_history"]
