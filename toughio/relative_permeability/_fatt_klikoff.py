from ._base import BaseRelativePermeability

__all__ = [
    "FattKlikoff",
]


class FattKlikoff(BaseRelativePermeability):
    _id = 6
    _name = "Fatt-Klikoff"

    def __init__(self, slr):
        """
        Fatt and Klikoff's function.

        After Fatt and Klikoff (1959).

        Parameters
        ----------
        slr : scalar
            Irreducible liquid saturation (RP(1)).

        """
        if slr >= 1.0:
            raise ValueError()
        self.parameters = [slr]

    def _eval(self, sl, *args):
        """Fatt and Klikoff's function."""
        (slr,) = args
        Seff = (sl - slr) / (1.0 - slr) if sl > slr else 0.0
        kl = Seff**3
        kg = (1.0 - Seff) ** 3
        return kl, kg

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._slr]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 1:
            raise ValueError()
        self._slr = value[0]
