from ._base import BaseCapillarity

__all__ = [
    "Milly",
]


class Milly(BaseCapillarity):
    _id = 4
    _name = "Milly"

    def __init__(self, slr):
        """
        Milly's function.

        After Milly (1982).

        Parameters
        ----------
        slr : scalar
            Irreducible liquid saturation (CP(1)).

        """
        if slr < 0.0:
            raise ValueError()
        self.parameters = [slr]

    def _eval(self, sl, *args):
        (slr,) = args
        sl = max(sl, 1.001 * slr)
        fac = (
            1.0
            if sl - slr >= 0.371
            else 10 ** (2.26 * (0.371 / (sl - slr) - 1.0) ** 0.25 - 2.0)
        )
        return -97.783 * fac

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._slr]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 1:
            raise ValueError()
        self._slr = value[0]
