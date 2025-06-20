from __future__ import annotations

from collections.abc import Callable
from typing import Literal
from numpy.typing import ArrayLike

import numpy as np


def thermal_expansion_coefficient(
    temperature: ArrayLike,
    density: Literal["brine", "water"] | Callable = "water",
    eps: float = 1.0e-8,
    *args,
    **kwargs
) -> ArrayLike:
    """
    Calculate the coefficient(s) of thermal expansion of water.

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
