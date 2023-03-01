from abc import ABCMeta, abstractmethod, abstractproperty

import numpy as np

__all__ = [
    "BaseRelativePermeability",
]


# See <https://stackoverflow.com/questions/35673474/using-abc-abcmeta-in-a-way-it-is-compatible-both-with-python-2-7-and-python-3-5>
ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class BaseRelativePermeability(ABC):
    _id = None
    _name = ""

    def __init__(self, *args):
        """
        Base class for relative permeability models.

        Do not use.

        """
        pass

    def __repr__(self):
        """Display relative permeability model informations."""
        out = [f"{self._name} relative permeability model (IRP = {self._id}):"]
        out += [
            f"    RP({i + 1}) = {parameter}"
            for i, parameter in enumerate(self.parameters)
        ]
        return "\n".join(out)

    def __call__(self, sl):
        """Calculate relative permeability given liquid saturation."""
        if np.ndim(sl) == 0:
            if not (0.0 <= sl <= 1.0):
                raise ValueError()
            return self._eval(sl, *self.parameters)
        else:
            sl = np.asarray(sl)
            if not np.logical_and((sl >= 0.0).all(), (sl <= 1.0).all()):
                raise ValueError()
            return np.transpose([self._eval(sat, *self.parameters) for sat in sl])

    @abstractmethod
    def _eval(self, sl, *args):
        raise NotImplementedError()

    def plot(self, n=100, ax=None, figsize=(10, 8), plt_kws=None):
        """
        Plot relative permeability curve.

        Parameters
        ----------
        n : int, optional, default 100
            Number of saturation points.
        ax : matplotlib.pyplot.Axes or None, optional, default None
            Matplotlib axes. If `None`, a new figure and axe is created.
        figsize : array_like or None, optional, default None
            New figure size if `ax` is `None`.
        plt_kws : dict or None, optional, default None
            Additional keywords passed to :func:`matplotlib.pyplot.plot`.

        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError(
                "Plotting relative permeability curve requires matplotlib to be installed."
            )

        if not (isinstance(n, int) and n > 1):
            raise TypeError()
        if not (ax is None or isinstance(ax, plt.Axes)):
            raise TypeError()
        if not (figsize is None or isinstance(figsize, (tuple, list, np.ndarray))):
            raise TypeError()
        if len(figsize) != 2:
            raise ValueError()
        if not (plt_kws is None or isinstance(plt_kws, dict)):
            raise TypeError()

        # Plot parameters
        plt_kws = plt_kws if plt_kws is not None else {}
        _kwargs = {"linestyle": "-", "linewidth": 2}
        _kwargs.update(plt_kws)

        # Initialize figure
        if ax:
            ax1 = ax
        else:
            figsize = figsize if figsize else (8, 5)
            fig = plt.figure(figsize=figsize, facecolor="white")
            ax1 = fig.add_subplot(1, 1, 1)

        # Calculate liquid and gas relative permeability
        sl = np.linspace(0.0, 1.0, n)
        kl, kg = self(sl)

        # Plot
        ax1.plot(sl, kl, label="Liquid", **_kwargs)
        ax1.plot(sl, kg, label="Gas", **_kwargs)
        ax1.set_xlim(0.0, 1.0)
        ax1.set_ylim(0.0, 1.0)
        ax1.set_xlabel("Saturation (liquid)")
        ax1.set_ylabel("Relative permeability")
        ax1.grid(True, linestyle=":")

        plt.draw()
        plt.show()
        return ax1

    @property
    def id(self):
        """Return relative permeability model ID in TOUGH."""
        return self._id

    @property
    def name(self):
        """Return relative permeability model name."""
        return self._name

    @abstractproperty
    def parameters(self):
        raise NotImplementedError()

    @parameters.setter
    def parameters(self, value):
        raise NotImplementedError()
