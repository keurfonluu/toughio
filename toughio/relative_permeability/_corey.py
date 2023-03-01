from ._base import BaseRelativePermeability

__all__ = [
    "Corey",
]


class Corey(BaseRelativePermeability):
    _id = 3
    _name = "Corey"

    def __init__(self, slr, sgr):
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
        if slr + sgr >= 1.0:
            raise ValueError()
        self.parameters = [slr, sgr]

    def _eval(self, sl, *args):
        """Corey's curve."""
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
            kg = (1.0 - Shat**2) * (1.0 - Shat) ** 2
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
