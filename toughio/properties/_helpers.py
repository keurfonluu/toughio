from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike


def conductivity_to_permeability(
    conductivity: ArrayLike,
    temperature: ArrayLike = 25.0,
    pressure: ArrayLike = 101325.0,
    gravity: ArrayLike = 9.80665,
) -> ArrayLike:
    """
    Convert hydraulic conductivity to intrinsic permeability.

    Parameters
    ----------
    conductivity : ArrayLike
        Hydraulic conductivity (in m/s).
    temperature : ArrayLike, default 25.0
        Temperature(s) (in °C).
    pressure : ArrayLike, default 101325.0
        Pressure(s) (in Pa).
    gravity : ArrayLike, default 9.80665
        Gravitational acceleration (in m/s²).

    Returns
    -------
    ArrayLike
        Intrinsic permeability (in m²).

    """
    from .water import density, viscosity

    rho = density(temperature, pressure)
    eta = viscosity(temperature, pressure)

    return conductivity * eta / (rho * gravity)


def thermal_expansion_coefficient(
    temperature: ArrayLike,
    density: Literal["brine", "water"] | Callable = "water",
    eps: float = 1.0e-8,
    *args,
    **kwargs,
) -> ArrayLike:
    """
    Calculate the coefficient(s) of thermal expansion.

    Parameters
    ----------
    temperature : ArrayLike
        Temperature(s) (in °C).
    density : {'brine', 'water'} | Callable, default 'water'
        Density function or identifier.
    pressure : float, default 101325.0
        Reference pressure (in Pa).
    eps : float, default 1.0e-8
        Temperature increment for numerical derivative.
    *args, **kwargs
        Additional arguments for the density function.

    Returns
    -------
    ArrayLike
        Coefficient(s) of thermal expansion (in 1/°C).

    """
    from . import brine, water

    if isinstance(density, str):
        if density == "brine":
            density = brine.density

        elif density == "water":
            density = water.density

        else:
            raise ValueError(f"invalid density function '{density}'")

    temperature = np.asanyarray(temperature)
    rho = lambda temp: density(temp, *args, **kwargs)
    drhodT = (rho(temperature + eps) - rho(temperature - eps)) / (2.0 * eps)

    return -drhodT / rho(temperature)
