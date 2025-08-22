from __future__ import annotations

from typing import Literal, Optional

import numpy as np
from numpy.typing import ArrayLike


def density(
    temperature: ArrayLike = 25.0,
    pressure: ArrayLike = 101325.0,
    method: Literal["IFC67"] = "IFC67",
) -> ArrayLike:
    """
    Calculate the density of water.

    Parameters
    ----------
    temperature : ArrayLike, default 25.0
        Temperature(s) (in °C).
    pressure : ArrayLike, default 101325.0
        Pressure(s) (in Pa).
    method : {'IFC67'}, default 'IFC67'
        Method to use for density calculation.

    Returns
    -------
    ArrayLike
        Density(ies) of water (in kg/m³).

    """
    temperature = np.asanyarray(temperature)
    pressure = np.asanyarray(pressure)

    if method == "IFC67":
        A = [
            6824.687741,
            -542.2063673,
            -20966.66205,
            39412.86787,
            -67332.77739,
            99023.81028,
            -109391.1774,
            85908.41667,
            -45111.68742,
            14181.38926,
            -2017.271113,
            7.982692717,
            -2.616571843e-2,
            1.52241179e-3,
            2.284279054e-2,
            242.1647003,
            1.269716088e-10,
            2.074838328e-7,
            2.17402035e-8,
            1.105710498e-9,
            12.93441934,
            1.308119072e-5,
            6.047626338e-14,
        ]
        SA = [
            0.8438375405,
            5.362162162e-4,
            1.72,
            7.342278489e-2,
            4.97585887e-2,
            0.6537154300,
            1.15e-6,
            1.1508e-5,
            0.14188,
            7.002753165,
            2.995284926e-4,
            0.204,
        ]
        TKR = (temperature + 273.15) / 647.3
        PNMR = pressure / 2.212e7
        TKR2, TKR8, TKR10 = TKR**2, TKR**8, TKR**10
        TKR11 = TKR * TKR10
        PNMR2 = PNMR**2

        Y = 1.0 - SA[0] * TKR2 - SA[1] / TKR**6
        ZP = SA[2] * Y**2 - 2.0 * SA[3] * TKR + 2.0 * SA[4] * PNMR

        if (ZP < 0.0).any():
            raise ValueError("could not calculate density at given temperature")

        PAR1 = A[11] * SA[4] / (Y + ZP**0.5) ** 0.294117647058824
        PAR2 = (
            A[12]
            + A[13] * TKR
            + A[14] * TKR2
            + A[15] * (SA[5] - TKR) ** 10
            + A[16] / (SA[6] + TKR8 * TKR11)
        )
        PAR3 = (A[17] + 2.0 * A[18] * PNMR + 3.0 * A[19] * PNMR2) / (SA[7] + TKR11)
        PAR4 = (
            A[20]
            * TKR8
            * TKR10
            * (SA[8] + TKR2)
            * (-3.0 / (SA[9] + PNMR) ** 4 + SA[10])
        )
        PAR5 = 3.0 * A[21] * (SA[11] - TKR) * PNMR2 + 4.0 * A[22] / TKR10**2 * PNMR**3
        V = (PAR1 + PAR2 - PAR3 - PAR4 + PAR5) * 3.17e-3

        return 1.0 / V

    else:
        raise ValueError(f"invalid method '{method}'")


def vapor_saturation_pressure(
    temperature: ArrayLike,
) -> ArrayLike:
    """
    Calculate vapor saturation pressure.

    Parameters
    ----------
    temperature : ArrayLike
        Temperature(s) (in °C).

    Returns
    -------
    ArrayLike
        Saturation pressure (in Pa).

    """
    A67 = [
        -7.691234564,
        -26.08023696,
        -168.1706546,
        6.423285504e1,
        -118.9646225,
        4.167117320,
        20.97506760,
        1.0e9,
        6.0,
    ]

    tc = (temperature + 273.15) / 647.3
    x1 = 1.0 - tc
    x2 = x1**2
    sc = A67[4] * x1 + A67[3]
    sc = sc * x1 + A67[2]
    sc = sc * x1 + A67[1]
    sc = sc * x1 + A67[0]
    sc *= x1
    pc = np.exp(
        sc / (tc * (1.0 + A67[5] * x1 + A67[6] * x2)) - x1 / (A67[7] * x2 + A67[8])
    )
    ps = pc * 2.212e7

    return ps


def viscosity(
    temperature: ArrayLike = 25.0,
    pressure: ArrayLike = 101325.0,
    saturation_pressure: Optional[ArrayLike] = None,
    kinematic: bool = False,
) -> ArrayLike:
    """
    Calculate the viscosity of water.

    Parameters
    ----------
    temperature : ArrayLike, default 25.0
        Temperature(s) (in °C).
    pressure : ArrayLike, default 101325.0
        Pressure(s) (in Pa).
    saturation_pressure : ArrayLike, optional
        Saturation pressure(s) (in Pa).
    kinematic : bool, default False
        If True, return kinematic viscosity (in m²/s) instead of dynamic viscosity (in Pa·s).

    Returns
    -------
    ArrayLike
        Dynamic viscosity (in Pa·s) or kinematic viscosity (in m²/s) of water.

    """
    temperature = np.asanyarray(temperature)
    pressure = np.asanyarray(pressure)
    saturation_pressure = (
        np.asanyarray(saturation_pressure)
        if saturation_pressure is not None
        else vapor_saturation_pressure(temperature)
    )

    phi = 1.0467 * (temperature - 31.85)
    fac = 1.0 + phi * (pressure - saturation_pressure) * 1.0e-11
    visco = 1.0e-7 * fac * 241.4 * 10.0 ** (247.8 / (temperature + 133.15))

    if kinematic:
        rho = density(temperature, pressure)
        visco /= rho

    return visco
