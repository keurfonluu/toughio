from ._base import BaseRelativePermeability

__all__ = [
    "Pickens",
]


class Pickens(BaseRelativePermeability):
    """Gas perfect mobile function.

    Parameters
    ----------
    x : scalar
        RP(1).

    """

    _id = 2
    _name = "Pickens"

    def __init__(self, x):
        self.parameters = [x]

    def _eval(self, sl, x):
        """Gas perfect mobile function."""
        return sl ** x, 1.0

    @property
    def parameters(self):
        """Return model parameters."""
        return [self._x]

    @parameters.setter
    def parameters(self, value):
        if len(value) != 1:
            raise ValueError()
        self._x = value[0]
