import os

import helpers
import matplotlib.pyplot as plt
import numpy as np
import pytest

import toughio

if not os.environ.get("DISPLAY", ""):
    plt.switch_backend("Agg")


@pytest.mark.parametrize(
    "model, parameters",
    [
        (toughio.relative_permeability.Linear, [0.2, 0.3, 0.8, 0.9]),
        (toughio.relative_permeability.Pickens, [2.0]),
        (toughio.relative_permeability.Corey, [0.3, 0.05]),
        (toughio.relative_permeability.Grant, [0.3, 0.05]),
        (toughio.relative_permeability.FattKlikoff, [0.3]),
        (toughio.relative_permeability.vanGenuchtenMualem, [0.457, 0.15, 1.0, 0.1]),
        (toughio.relative_permeability.Verma, []),
    ],
)
def test_relative_permeability(model, parameters, monkeypatch):
    import json

    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        this_dir, "support_files", "relative_permeability_references.json"
    )
    with open(filename, "r") as f:
        relperm_ref = json.load(f)

    sl = np.linspace(0.0, 1.0, 201)

    perm = model(*parameters)
    relperm = np.transpose(perm(sl))

    assert helpers.allclose(relperm, relperm_ref[perm.name])

    monkeypatch.setattr(plt, "show", lambda: None)
    perm.plot()

    print(perm)
