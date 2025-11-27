from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import ArrayLike, NDArray


class BaseCurve(ABC):
    """Base class for curve models."""

    _id: int
    _name: str
    _short: str

    def __init__(self, *args) -> None:
        """Initialize a curve."""
        self.parameters = args

    def __repr__(self) -> str:
        """Display curve informations."""
        out = [
            f"{self.name} {self.__class__.__name__.lower()} model (I{self._short} = {self.id}):"
        ]
        out += [
            f"    {self._short}({i + 1}) = {parameter}"
            for i, parameter in enumerate(self.parameters)
        ]

        return "\n".join(out)

    def __call__(self, sl: ArrayLike) -> NDArray:
        """Compute curve data given liquid saturation."""
        sl = np.asanyarray(sl)

        if np.logical_and(sl < 0.0, sl > 1.0).any():
            raise ValueError("liquid saturation must be between 0.0 and 1.0")

        return self._eval(sl, *self.parameters)

    @abstractmethod
    def _eval(self, sl: ArrayLike, *args) -> NDArray: ...

    @abstractmethod
    def plot(*args) -> None: ...

    @property
    def id(self) -> int:
        """Return model ID."""
        return self._id

    @property
    def name(self) -> str:
        """Return model name."""
        return self._name

    @property
    def parameters(self) -> list[float]:
        """Return model parameters."""
        return self._parameters

    @parameters.setter
    def parameters(self, value: Sequence[float]) -> None:
        """Set model parameters."""
        self._parameters = list(value)
