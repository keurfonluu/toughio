from ._base import BaseRelativePermeability

__all__ = [
    "Verma",
]


class Verma(BaseRelativePermeability):
    _id = 8
    _name = "Verma"

    def __init__(self, slr=0.2, sls=0.895, a=1.259, b=-1.7615, c=0.5089):
        """
        Verma's function.

        After Verma et al. (1985).

        Parameters
        ----------
        slr : scalar
            Irreducible liquid saturation (RP(1)).
        sls : scalar
            Maximum liquid saturation (RP(2)).
        a : scalar
            A (RP(3)).
        b : scalar
            B (RP(4)).
        c : scalar
            C (RP(5)).

        """
        self.parameters = [slr, sls, a, b, c]

    def _eval(self, sl, *args):
        """Verma's function."""
        slr, sls, a, b, c = args
        Shat = (sl - slr) / (sls - slr)
        Shat = max(Shat, 0.0)
        Shat = min(Shat, 1.0)
        kl = Shat**3
        kg = a + b * Shat + c * Shat**2
        kg = max(kg, 0.0)
        kg = min(kg, 1.0)
        return kl, kg

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._slr, self._sls, self._a, self._b, self._c]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 5:
            raise ValueError()
        self._slr = value[0]
        self._sls = value[1]
        self._a = value[2]
        self._b = value[3]
        self._c = value[4]
