from __future__ import annotations

from typing import Literal
from numpy.typing import ArrayLike

import numpy as np


def density(
    temperature: ArrayLike,
    pressure: ArrayLike,
    salt_mass_fraction: ArrayLike,
    method: Literal["STOMP"] = "STOMP",
) -> ArrayLike:
    """
    Calculate the density of brine.
    
    Parameters
    ----------
    temperature : ArrayLike
        Temperature (in °C, <= 350.0).
    pressure : ArrayLike
        Pressure (in Pa, <= 1.0e8).
    salt_mass_fraction : ArrayLike
        Salt mass fraction.
    method : {'STOMP'}, default 'STOMP'
        Method to use for density calculation.

    Returns
    -------
    ArrayLike
        Density(ies) of brine (in kg/m³).

    References
    ----------
    .. [1] Haas Jr., J. L. (1976).
        "Physical Properties of the Coexisting Phases and Thermochemical Properties
        of the H2O Component in Boiling NaCl Solutions. Preliminary Steam Tables
        for NaCl Solutions". Geological Survey Bulletin 1421-A.

    .. [2] Phillips, S. L., Ozbek, H., and Silvester, L. F. (1983).
        "Density of Sodium Chloride Solutions at High Temperatures and Pressures".
        LBL-16275, Lawrence Berkeley Laboratory, University of California, Berkeley, California.

    """
    from . import water

    temperature = np.asanyarray(temperature)
    pressure = np.asanyarray(pressure)
    salt_mass_fraction = np.asanyarray(salt_mass_fraction)

    if method == "STOMP":
        Mw_salt = 58.4428  # salt molar mass (g/mol)
        CHX = np.poly1d([-261.07, 448.55, -167.219])

        # Convert mass fraction to molality
        bsalt = 1.0e3 * salt_mass_fraction / (Mw_salt * (1.0 - salt_mass_fraction))

        # Compressed or vapor-saturated density of pure water using the ASME formulations
        pressure = np.maximum(pressure, water.vapor_saturation_pressure(temperature))
        rhow = water.density(temperature, pressure)
        rhowi = 1.0e3 / rhow

        # Equation (2.19)
        phi = CHX(rhowi) + (-13.644 + 13.97 * rhowi) * (rhowi / (3.1975 - rhowi)) ** 2 * np.sqrt(bsalt)
        rhob = (1.0e3 + bsalt * Mw_salt) / (1.0e3 * rhowi + phi * bsalt) * 1.0e3

    else:
        raise ValueError(f"invalid method '{method}'")

    return rhob
