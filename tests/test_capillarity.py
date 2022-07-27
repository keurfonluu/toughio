import os

import helpers
import matplotlib.pyplot as plt
import numpy as np
import pytest

import toughio

if not os.environ.get("DISPLAY", ""):
    plt.switch_backend("Agg")


@pytest.mark.parametrize(
    "model, parameters, sl",
    [
        (toughio.capillarity.Linear, [1.0e6, 0.25, 0.4], None),
        (toughio.capillarity.Pickens, [1.0e6, 0.3, 1.3, 0.8], None),
        (
            toughio.capillarity.TRUST,
            [1.0e6, 0.3, 1.3, 0.8, 1.0e7],
            np.linspace(0.02, 1.0, 50),
        ),
        (toughio.capillarity.Milly, [0.25], None),
        (
            toughio.capillarity.vanGenuchten,
            [0.457, 0.0, 5.105e-4, 1.0e7, 1.0],
            np.linspace(0.02, 1.0, 50),
        ),
    ],
)
def test_capillarity(model, parameters, sl, monkeypatch):
    import json

    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "capillarity_references.json")
    with open(filename, "r") as f:
        pcap_ref = json.load(f)

    sl = np.linspace(0.0, 1.0, 51) if sl is None else sl

    cap = model(*parameters)
    pcap = cap(sl)
    assert helpers.allclose(pcap, pcap_ref[cap.name][: len(pcap)])

    monkeypatch.setattr(plt, "show", lambda: None)
    cap.plot()

    print(cap)
