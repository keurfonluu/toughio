import numpy as np

from ...output.tecplot._tecplot import read_buffer
from ...._common import open_file


def read(filename):
    """Read TECPLOT line plots."""
    with open_file(filename, "r") as f:
        headers, zones = read_buffer(f)

    out = {headers[0]: zones[0]["data"][:, 0]}
    for zone in zones:
        out[zone["title"]] = zone["data"][:, 1]

    return out
