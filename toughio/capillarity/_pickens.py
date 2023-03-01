import numpy as np

from ._base import BaseCapillarity

__all__ = [
    "Pickens",
]


class Pickens(BaseCapillarity):
    _id = 2
    _name = "Pickens"

    def __init__(self, p0, slr, sl0, x):
        """
        Pickens et al. function.

        After Pickens et al. (1979).

        Parameters
        ----------
        p0 : scalar
            Capillary pressure strength (CP(1)).
        slr : scalar
            Irreducible liquid saturation (CP(2)).
        sl0 : scalar
            Initial liquid saturation (CP(3)).
        x : scalar
            CP(4).

        """
        if not (0.0 < slr < 1.0):
            raise ValueError()
        if sl0 < 1.0:
            raise ValueError()
        if x == 0.0:
            raise ValueError()
        self.parameters = [p0, slr, sl0, x]

    def _eval(self, sl, *args):
        """Pickens et al function."""
        p0, slr, sl0, x = args
        sl = max(sl, 1.001 * slr)
        sl = 0.999 * sl0 if sl > 0.999 * sl0 else sl

        A = (1.0 + sl / sl0) * (sl0 - slr) / (sl0 + slr)
        B = 1.0 - sl / sl0
        return -p0 * (np.log(A / B * (1.0 + (1.0 - B**2 / A**2) ** 0.5))) ** (
            1.0 / x
        )

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._p0, self._slr, self._sl0, self._x]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 4:
            raise ValueError()
        self._p0 = value[0]
        self._slr = value[1]
        self._sl0 = value[2]
        self._x = value[3]
