from ._base import BaseRelativePermeability

__all__ = [
    "Linear",
]


class Linear(BaseRelativePermeability):
    """Linear function.

    Parameters
    ----------
    slmin : scalar
        Lower liquid saturation threshold (CP(1)).
    sgmin : scalar
        Lower gas saturation threshold (CP(2)).
    slmax : scalar
        Upper liquid saturation threshold (CP(3)).
    sgmax : scalar
        Upper gas saturation threshold (CP(4)).

    """

    _id = 1
    _name = "Linear"

    def __init__(self, slmin, sgmin, slmax, sgmax):
        assert slmin < slmax
        assert sgmin < sgmax
        self.parameters = [slmin, sgmin, slmax, sgmax]

    def _eval(self, sl, slmin, sgmin, slmax, sgmax):
        """Linear function."""
        kl = (
            1.0
            if sl >= slmax
            else 0.0
            if sl <= slmin
            else (sl - slmin) / (slmax - slmin)
        )

        sg = 1.0 - sl
        kg = (
            1.0
            if sg >= sgmax
            else 0.0
            if sg <= sgmin
            else (sg - sgmin) / (sgmax - sgmin)
        )

        return kl, kg

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._slmin, self._sgmin, self._slmax, self._sgmax]

    @parameters.setter
    def parameters(self, value):
        assert len(value) == 4
        self._slmin = value[0]
        self._sgmin = value[1]
        self._slmax = value[2]
        self._sgmax = value[3]
