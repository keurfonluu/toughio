from ._base import BaseCapillarity

__all__ = [
    "Linear",
]


class Linear(BaseCapillarity):
    _id = 1
    _name = "Linear"

    def __init__(self, pmax, smin, smax):
        """
        Linear function.

        Parameters
        ----------
        pmax : scalar
            Maximum pressure (CP(1)).
        smin : scalar
            Lower liquid saturation threshold (CP(2)).
        smax : scalar
            Upper liquid saturation threshold (CP(3)).

        """
        if smax <= smin:
            raise ValueError()
        self.parameters = [pmax, smin, smax]

    def _eval(self, sl, *args):
        """Linear function."""
        pmax, smin, smax = args
        return (
            -pmax
            if sl <= smin
            else 0.0
            if sl >= smax
            else -pmax * (smax - sl) / (smax - smin)
        )

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._pmax, self._smin, self._smax]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 3:
            raise ValueError()
        self._pmax = value[0]
        self._smin = value[1]
        self._smax = value[2]
