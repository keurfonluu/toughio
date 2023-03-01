from ._base import BaseCapillarity

__all__ = [
    "vanGenuchten",
]


class vanGenuchten(BaseCapillarity):
    _id = 7
    _name = "van Genuchten"

    def __init__(self, m, slr, alpha, pmax, sls):
        """
        Van Genuchten function.

        After van Genuchten (1980).

        Parameters
        ----------
        m : scalar
            Related to pore size distribution (CP(1)).
        slr : scalar
            Irreducible liquid saturation (CP(2)).
        alpha : scalar
            Inverse of capillary pressure strength 1/P0 (CP(3)).
        pmax : scalar
            Maximum pressure (CP(4)).
        sls : scalar
            Maximum liquid saturation (CP(5)).

        """
        if pmax < 0.0:
            raise ValueError()
        self.parameters = [m, slr, alpha, pmax, sls]

    def _eval(self, sl, *args):
        """Van Genuchten function."""
        m, slr, alpha, pmax, sls = args
        if sl == 1.0:
            pcap = 0.0
        else:
            if sl > slr:
                Seff = (sl - slr) / (sls - slr)
                pcap = -1.0 / abs(alpha) * (Seff ** (-1.0 / m) - 1.0) ** (1.0 - m)
            else:
                pcap = -abs(pmax)
            pcap = max(pcap, -abs(pmax))
            pcap *= (1.0 - sl) / 0.001 if sl > 0.999 else 1.0
        return pcap

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._m, self._slr, self._alpha, self._pmax, self._sls]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 5:
            raise ValueError()
        self._m = value[0]
        self._slr = value[1]
        self._alpha = value[2]
        self._pmax = value[3]
        self._sls = value[4]
