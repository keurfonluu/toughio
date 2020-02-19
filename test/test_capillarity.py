import numpy

import helpers
import toughio


def test_linear():
    helpers.capillarity(
        model=toughio.capillarity.Linear, parameters=[1.0e6, 0.25, 0.4],
    )


def test_pickens():
    helpers.capillarity(
        model=toughio.capillarity.Pickens, parameters=[1.0e6, 0.3, 1.3, 0.8],
    )


def test_trust():
    helpers.capillarity(
        model=toughio.capillarity.TRUST,
        parameters=[1.0e6, 0.3, 1.3, 0.8, 1.0e7],
        sl=numpy.linspace(0.02, 1.0, 50),
    )


def test_milly():
    helpers.capillarity(
        model=toughio.capillarity.Milly, parameters=[0.25],
    )


def test_vanGenuchten():
    helpers.capillarity(
        model=toughio.capillarity.vanGenuchten,
        parameters=[0.457, 0.0, 5.105e-4, 1.0e7, 1.0],
        sl=numpy.linspace(0.02, 1.0, 50),
    )
