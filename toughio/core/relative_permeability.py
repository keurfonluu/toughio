from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ._curve import BaseCurve


if TYPE_CHECKING:
    from typing import Optional

    from numpy.typing import ArrayLike, NDArray


class RelativePermeabilityModel(BaseCurve):
    """Base class for relative permeability model."""

    _short = "RP"

    def _eval(self, sl: ArrayLike, *args) -> None: ...

    def plot(self, n: int = 100, ax: Optional[Axes] = None, **kwargs) -> None:
        """
        Plot relative permeability curve.

        Parameters
        ----------
        n : int, default 100
            Number of saturation points.
        ax : matplotlib.axes.Axes, optional
            Plot axes.
        **kwargs : dict, optional
            Additional keyword arguments. See ``matplotlib.pyplot.plot`` for more details.

        """
        # Calculate liquid and gas relative permeability
        sl = np.linspace(0.0, 1.0, n)
        kl, kg = self(sl)

        # Plot
        ax = ax if ax is not None else plt.gca()

        ax.plot(sl, kl, label="Liquid", **kwargs)
        ax.plot(sl, kg, label="Gas", **kwargs)
        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.0)
        ax.set_xlabel("Saturation (liquid)")
        ax.set_ylabel("Relative permeability")


class Linear(RelativePermeabilityModel):
    """
    Linear function.

    Parameters
    ----------
    slmin : scalar
        Lower liquid saturation threshold (RP(1)).
    sgmin : scalar
        Lower gas saturation threshold (RP(2)).
    slmax : scalar
        Upper liquid saturation threshold (RP(3)).
    sgmax : scalar
        Upper gas saturation threshold (RP(4)).

    """

    def __init__(self, slmin: float, sgmin: float, slmax: float, sgmax: float) -> None:
        """Initialize linear relative permeability model."""
        if slmin >= slmax:
            raise ValueError("slmin must be lower than slmax")

        if sgmin >= sgmax:
            raise ValueError("sgmin must be lower than sgmax")

        super().__init__(slmin, sgmin, slmax, sgmax)
        self._id = 1
        self._name = "Linear"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Linear function."""
        sl = np.asanyarray(sl)
        slmin, sgmin, slmax, sgmax = args
        sg = 1.0 - sl

        mask = np.logical_and(sl > slmin, sl < slmax)
        kl = np.zeros_like(sl)
        kl[mask] = (sl[mask] - slmin) / (slmax - slmin)
        kl[sl >= slmax] = 1.0

        mask = np.logical_and(sg > sgmin, sg < sgmax)
        kg = np.zeros_like(sl)
        kg[mask] = (sg[mask] - sgmin) / (sgmax - sgmin)
        kg[sg >= sgmax] = 1.0

        return kl, kg


class Pickens(RelativePermeabilityModel):
    """
    Gas perfect mobile function.

    Parameters
    ----------
    x : scalar
        RP(1).

    """

    def __init__(self, x: float) -> None:
        """Initialize Pickens' relative permeability model."""
        super().__init__(x)
        self._id = 2
        self._name = "Pickens"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Gas perfect mobile function."""
        sl = np.asanyarray(sl)
        (x,) = args

        kl = np.power(sl, x)
        kg = np.ones_like(sl)

        return kl, kg


class Corey(RelativePermeabilityModel):
    """
    Corey's curve.

    After Corey (1954).

    Parameters
    ----------
    slr : scalar
        Irreducible liquid saturation (RP(1)).
    sgr : scalar
        Irreducible gas saturation (RP(2)).

    """

    def __init__(self, slr: float, sgr: float) -> None:
        """Initialize Corey's relative permeability model."""
        if slr + sgr >= 1.0:
            raise ValueError("slr + sgr must be lower than 1.0")

        super().__init__(slr, sgr)
        self._id = 3
        self._name = "Corey"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Corey's curve."""
        sl = np.asanyarray(sl)
        slr, sgr = args
        sg = 1.0 - sl

        mask = np.logical_and(sg >= sgr, sg < 1.0 - slr)
        Shat = (sl[mask] - slr) / (1.0 - slr - sgr)

        kl = np.zeros_like(sl)
        kl[mask] = np.power(Shat, 4)
        kl[sg < sgr] = 1.0

        kg = np.zeros_like(sl)
        kg[mask] = (1.0 - Shat**2) * (1.0 - Shat) ** 2
        kg[sg >= 1.0 - slr] = 1.0

        return kl, kg


class Grant(RelativePermeabilityModel):
    """
    Grant's curve.

    After Grant (1977).

    Parameters
    ----------
    slr : scalar
        Irreducible liquid saturation (RP(1)).
    sgr : scalar
        Irreducible gas saturation (RP(2)).

    """

    def __init__(self, slr: float, sgr: float) -> None:
        """Initialize Grant's relative permeability model."""
        if slr + sgr >= 1.0:
            raise ValueError("slr + sgr must be lower than 1.0")

        super().__init__(slr, sgr)
        self._id = 4
        self._name = "Grant"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Grant's curve."""
        sl = np.asanyarray(sl)
        slr, sgr = args
        sg = 1.0 - sl

        mask = np.logical_and(sg >= sgr, sg < 1.0 - slr)
        Shat = (sl[mask] - slr) / (1.0 - slr - sgr)

        kl = np.zeros_like(sl)
        kl[mask] = np.power(Shat, 4)
        kl[sg < sgr] = 1.0

        kg = np.zeros_like(sl)
        kg[mask] = 1.0 - kl[mask]
        kg[sg >= 1.0 - slr] = 1.0

        return kl, kg


class FattKlikoff(RelativePermeabilityModel):
    """
    Fatt and Klikoff's function.

    After Fatt and Klikoff (1959).

    Parameters
    ----------
    slr : scalar
        Irreducible liquid saturation (RP(1)).

    """

    def __init__(self, slr: float) -> None:
        """Initialize Fatt and Klikoff's relative permeability model."""
        if slr >= 1.0:
            raise ValueError("slr must be lower than 1.0")

        super().__init__(slr)
        self._id = 6
        self._name = "Fatt-Klikoff"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Fatt and Klikoff's function."""
        sl = np.asanyarray(sl)
        (slr,) = args

        mask = sl > slr
        Seff = np.zeros_like(sl)
        Seff[mask] = (sl[mask] - slr) / (1.0 - slr)

        kl = np.power(Seff, 3)
        kg = np.power(1.0 - Seff, 3)

        return kl, kg


class vanGenuchtenModified(RelativePermeabilityModel):
    """
    Modified van Genuchten's function.

    After Luckner et al. (1989).

    Parameters
    ----------
    m : scalar
        Related to pore size distribution (CP(4) or 1 - 1/CP(1)).
    slrk : scalar
        Irreducible liquid saturation (RP(1)).
    sgr : scalar
        Irreducible gas saturation (RP(2)).
    flag : scalar, default 0.0
        Flag for gas relative permeability model (RP(3)).
    eta : scalar, default 0.5
        Exponent for liquid relative permeability (RP(4)).
    eps : scalar, default 0.0
        Linear extension near full saturation (RP(5)).
    zeta : scalar, default 1/3
        Exponent for gas relative permeability (RP(7)).

    Notes
    -----
    Active Fracture Model parameters are not supported (i.e., RP(6) is None, gamma is
    zero).

    """

    def __init__(
        self,
        m: float,
        slrk: float,
        sgr: float,
        flag: float = 0.0,
        eta: float = 0.5,
        eps: float = 0.0,
        zeta: float = 1.0 / 3.0,
    ) -> None:
        """Initialize modified van Genuchten's relative permeability model."""
        super().__init__(slrk, sgr, flag, eta, eps, None, zeta)
        self._id = 11
        self._name = "Modified van Genuchten"
        self._m = m

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Modified van Genuchten's function."""
        sl = np.asanyarray(sl)
        slrk, sgr, flag, eta, eps, _, zeta = args
        m = self._m

        eta = 0.5 if eta == 0.0 else eta
        zeta = 1.0 / 3.0 if zeta == 0.0 else zeta

        # Liquid relative permeability
        Sekl = (sl - slrk) / (1.0 - slrk)

        kl = np.zeros_like(sl)
        kl[Sekl >= 1.0] = 1.0

        mask = np.logical_and(Sekl > 0.0, Sekl <= 1.0 - eps)
        if mask.any():
            kl[mask] = (
                Sekl[mask] ** eta * (1.0 - (1.0 - Sekl[mask] ** (1.0 / m)) ** m) ** 2
            )

        mask = np.logical_and(Sekl > 1.0 - eps, Sekl < 1.0)
        if mask.any():
            c1 = 1.0 - eps
            c2 = c1**eta * (1.0 - (1.0 - c1 ** (1.0 / m)) ** m) ** 2
            kl[mask] = c2 + (Sekl[mask] - c1) * (1.0 - c2) / eps

        # Gas relative permeability
        if flag > 1.0e-10:
            kg = 1.0 - kl

        else:
            Sekg = sl / (1.0 - sgr)

            kg = np.zeros_like(sl)
            kg[Sekg < 0.0] = 1.0

            mask = np.logical_and(Sekg >= 0.0, Sekg <= 1.0)
            if mask.any():
                kg = (1.0 - Sekg[mask]) ** zeta * (1.0 - Sekg[mask] ** (1.0 / m)) ** (
                    2 * m
                )

        return kl, kg


class vanGenuchtenMualem(RelativePermeabilityModel):
    """
    van Genuchten-Mualem's function.

    After Mualem (1976) and van Genuchten (1980).

    Parameters
    ----------
    m : scalar
        Related to pore size distribution (RP(1)).
    slr : scalar
        Irreducible liquid saturation (RP(2)).
    sls : scalar
        Maximum liquid saturation (RP(3)).
    sgr : scalar
        Irreducible gas saturation (RP(4)).

    """

    def __init__(self, m: float, slr: float, sls: float, sgr: float) -> None:
        """Initialize van Genuchten-Mualem's relative permeability model."""
        super().__init__(m, slr, sls, sgr)
        self._id = 7
        self._name = "van Genuchten-Mualem"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Van Genuchten-Mualem's function."""
        sl = np.asanyarray(sl)
        m, slr, sls, sgr = args

        Seff = (sl - slr) / (sls - slr)
        mask = Seff > 0.0
        kl = np.zeros_like(sl)
        kl[mask] = Seff[mask] ** 0.5 * (1.0 - (1.0 - Seff[mask] ** (1.0 / m)) ** m) ** 2
        kl[sl >= sls] = 1.0

        Shat = ((sl - slr) / (1.0 - slr - sgr)).clip(0.0, 1.0)
        kg = np.where(sgr > 0.0, (1.0 - Shat**2) * (1.0 - Shat) ** 2, 1.0 - kl)
        kg[sl >= sls] = 0.0

        return kl, kg


class Verma(RelativePermeabilityModel):
    """
    Verma's function.

    After Verma et al. (1985).

    Parameters
    ----------
    slr : scalar, default 0.2
        Irreducible liquid saturation (RP(1)).
    sls : scalar, default 0.895
        Maximum liquid saturation (RP(2)).
    a : scalar, default 1.259
        A (RP(3)).
    b : scalar, default -1.7615
        B (RP(4)).
    c : scalar, default 0.5089
        C (RP(5)).

    """

    def __init__(
        self,
        slr: float = 0.2,
        sls: float = 0.895,
        a: float = 1.259,
        b: float = -1.7615,
        c: float = 0.5089,
    ) -> None:
        super().__init__(slr, sls, a, b, c)
        self._id = 8
        self._name = "Verma"

    def _eval(self, sl: ArrayLike, *args) -> tuple[NDArray, NDArray]:
        """Verma's function."""
        sl = np.asanyarray(sl)
        slr, sls, a, b, c = args

        Shat = ((sl - slr) / (sls - slr)).clip(0.0, 1.0)
        kl = np.power(Shat, 3)
        kg = (a + b * Shat + c * Shat**2).clip(0.0, 1.0)

        return kl, kg
