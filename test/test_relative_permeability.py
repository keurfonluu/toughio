import helpers
import toughio


def test_linear():
    helpers.relative_permeability(
        model=toughio.relative_permeability.Linear, parameters=[0.2, 0.3, 0.8, 0.9],
    )


def test_pickens():
    helpers.relative_permeability(
        model=toughio.relative_permeability.Pickens, parameters=[2.0],
    )


def test_corey():
    helpers.relative_permeability(
        model=toughio.relative_permeability.Corey, parameters=[0.3, 0.05],
    )


def test_grant():
    helpers.relative_permeability(
        model=toughio.relative_permeability.Grant, parameters=[0.3, 0.05],
    )


def test_fatt_klikoff():
    helpers.relative_permeability(
        model=toughio.relative_permeability.FattKlikoff, parameters=[0.3],
    )


def test_vanGenuchten_mualem():
    helpers.relative_permeability(
        model=toughio.relative_permeability.vanGenuchtenMualem,
        parameters=[0.457, 0.15, 1.0, 0.1],
    )


def test_verma():
    helpers.relative_permeability(
        model=toughio.relative_permeability.Verma, parameters=[],
    )
