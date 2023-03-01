from ._base import BaseRelativePermeability

__all__ = [
    "vanGenuchtenMualem",
]


class vanGenuchtenMualem(BaseRelativePermeability):
    _id = 7
    _name = "van Genuchten-Mualem"

    def __init__(self, m, slr, sls, sgr):
        """
        Van Genuchten-Mualem function.

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
        self.parameters = [m, slr, sls, sgr]

    def _eval(self, sl, *args):
        """Van Genuchten-Mualem function."""
        m, slr, sls, sgr = args
        if sl >= sls:
            kl = 1.0
            kg = 0.0

        else:
            Seff = (sl - slr) / (sls - slr)
            kl = (
                Seff**0.5 * (1.0 - (1.0 - Seff ** (1.0 / m)) ** m) ** 2
                if Seff > 0.0
                else 0.0
            )

            Shat = (sl - slr) / (1.0 - slr - sgr)
            Shat = max(Shat, 0.0)
            Shat = min(Shat, 1.0)
            kg = 1.0 - kl if sgr <= 0.0 else (1.0 - Shat**2) * (1.0 - Shat) ** 2

        return kl, kg

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._m, self._slr, self._sls, self._sgr]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 4:
            raise ValueError()
        self._m = value[0]
        self._slr = value[1]
        self._sls = value[2]
        self._sgr = value[3]
