from ._base import BaseCapillarity

__all__ = [
    "TRUST",
]


class TRUST(BaseCapillarity):
    _id = 3
    _name = "TRUST"

    def __init__(self, p0, slr, eta, pe, pmax):
        """
        TRUST capillary pressure.

        After Narasimhan et al. (1978).

        Parameters
        ----------
        p0 : scalar
            Capillary pressure strength (CP(1)).
        slr : scalar
            Irreducible liquid saturation (CP(2)).
        eta : scalar
            CP(3).
        pe : scalar
            Capillary entry pressure (CP(4)).
        pmax : scalar
            Maximum pressure (CP(5)).

        """
        if slr < 0.0:
            raise ValueError()
        if eta == 0.0:
            raise ValueError()
        self.parameters = [p0, slr, eta, pe, pmax]

    def _eval(self, sl, *args):
        """TRUST capillary pressure."""
        p0, slr, eta, pe, pmax = args
        if sl > slr:
            pcap = -pe - p0 * ((1.0 - sl) / (sl - slr)) ** (1.0 / eta)
        else:
            pcap = -abs(pmax)
        pcap = max(pcap, -abs(pmax))
        pcap *= (1.0 - sl) / 0.001 if sl > 0.999 else 1.0
        return pcap

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._p0, self._slr, self._eta, self._pe, self._pmax]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 5:
            raise ValueError()
        self._p0 = value[0]
        self._slr = value[1]
        self._eta = value[2]
        self._pe = value[3]
        self._pmax = value[4]
