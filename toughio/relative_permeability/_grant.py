from ._base import BaseRelativePermeability

__all__ = [
    "Grant",
]


class Grant(BaseRelativePermeability):
    _id = 4
    _name = "Grant"

    def __init__(self, slr, sgr):
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
        if slr + sgr >= 1.0:
            raise ValueError()
        self.parameters = [slr, sgr]

    def _eval(self, sl, *args):
        """Grant's curve."""
        slr, sgr = args
        sg = 1.0 - sl
        if sg < sgr:
            kl = 1.0
            kg = 0.0
        elif sg >= 1.0 - slr:
            kl = 0.0
            kg = 1.0
        else:
            Shat = (sl - slr) / (1.0 - slr - sgr)
            kl = Shat**4
            kg = 1.0 - kl
        return kl, kg

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._slr, self._sgr]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 2:
            raise ValueError()
        self._slr = value[0]
        self._sgr = value[1]
