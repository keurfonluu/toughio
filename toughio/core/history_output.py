from __future__ import annotations

import copy
import re
from collections import UserDict
from collections.abc import Sequence
from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from numpy.typing import ArrayLike
from typing_extensions import Self


class HistoryOutput(UserDict):
    """
    History output class.

    Parameters
    ----------
    obj : dict, optional
        Data dict.
    metadata : dict, optional
        Output metadata.

    """

    __name__: str = "HistoryOutput"
    __qualname__: str = "toughio.HistoryOutput"

    def __init__(
        self,
        obj: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Initialize an history output."""
        self.metadata = metadata
        super().__init__(obj if obj else {})

    def _repr_html_(self) -> str:
        """Represent an history output as an HTML dataframe."""
        return (
            self.to_dataframe()._repr_html_()
            if self.ndim
            else repr(self)
        )

    def __contains__(self, key: str) -> bool:
        """Return True if history output contains a key."""
        if super().__contains__(key):
            return True

        else:
            key, unit = self._get_key_unit(key)

            if unit and self.units[key] != unit:
                return False

            return key in set(self.keys())

    def __getitem__(self, key: str) -> ArrayLike:
        """Slice an history output."""
        try:
            return super().__getitem__(key)

        except KeyError:
            key, unit = self._get_key_unit(key)

            return super().__getitem__(key)

    def __setitem__(self, key: str, value: ArrayLike) -> None:
        """Add data to an history output."""
        # Check dimension
        ndim = self.ndim

        if ndim is not None and np.ndim(value) != ndim:
            raise ValueError(f"could not add data '{key}' with dim {np.ndim(value)} (expected dim {ndim})")

        # Check size
        size = self.size

        if size is not None and np.size(value) != size:
            raise ValueError(f"could not add data '{key}' with size {np.size(value)} (expected size {size})")

        # Add data
        key, unit = self._get_key_unit(key)
        value = np.asarray(value) if ndim == 1 else value
        super().__setitem__(key, value)

        # Add unit
        if unit:
            if not isinstance(unit, str):
                raise ValueError(f"invalid unit {unit}")

            self.units[key] = unit

    def __add__(self, obj: HistoryOutput) -> HistoryOutput:
        """Concatenate two history outputs."""
        return self.concatenate(obj, shift=False)

    def __iadd__(self, obj: HistoryOutput) -> Self:
        """Concatenate two history outputs in-place."""
        out = self.__add__(obj)
        self.clear()
        self.update(out)
        
        for k, v in obj.metadata.items():
            if k in self.metadata and isinstance(v, dict):
                self.metadata[k].update(v)

            else:
                self.metadata[k] = copy.deepcopy(v)

        return self

    def __call__(self, x: ArrayLike) -> HistoryOutput:
        """Interpolate an history output."""
        xp = self.time

        if xp is None or np.size(xp) == 1:
            raise ValueError("could not interpolate history output with scalar time data")

        out = {
            key: np.interp(x, xp, value, left=np.nan, right=np.nan)
            for key, value in self.to_dict(unit=True).items()
        }

        return HistoryOutput(out)

    def add_data(self, name: str, data: ArrayLike, unit: Optional[str] = None) -> None:
        """
        Add data to the history output.

        Parameters
        ----------
        name : str
            Data name.
        data : ArrayLike
            Data values.
        unit : str, optional
            Data unit.

        """
        self.data[name] = data
        self.units[name] = unit

    def copy(self, deep: bool = True) -> Self:
        """
        Return a copy of the history output.

        Parameters
        ----------
        deep : bool, default True
            If True, return a deep copy.

        Returns
        -------
        toughio.HistoryOutput
            Copy of the history output.

        """
        copy_ = copy.deepcopy if deep else copy.copy

        return self.__class__(copy_(self), copy_(self.metadata))

    def items(self, unit: bool = False) -> tuple[str, ArrayLike] | tuple[str, ArrayLike, str | None]:
        """
        Iterate over (key, value) pairs or (key, value, unit) trios.

        Parameters
        ----------
        unit : bool, default False
            If True, iterate over (key, value, unit) trios, otherwise (key, value) pairs.

        Yields
        ------
        str
            History data key.
        ArrayLike
            History data value.
        str | None
            History data unit. Only provided if *unit* is True.

        """
        if unit:
            for key, value in super().items():
                try:
                    unit = self.units[key]

                except KeyError:
                    unit = None

                yield key, value, unit

        else:
            for key, value in super().items():
                yield key, value

    def concatenate(self, obj: HistoryOutput | Sequence[HistoryOutput], shift: bool = False) -> HistoryOutput:
        """
        Concatenate history outputs.

        Parameters
        ----------
        obj : toughio.HistoryOutput | Sequence[toughio.HistoryOutput]
            History output(s) to concatenate this output with.
        shift : bool, default False
            If True, shift times of *obj* by the last time value of this output.
        
        Returns
        -------
        toughio.HistoryOutput
            Concatenated history output.

        """
        if not self:
            return obj.copy()

        elif not obj:
            return self.copy()
        
        elif isinstance(obj, HistoryOutput):
            obj1, obj2 = self, obj
            time1, time2 = obj1.time, obj2.time

            if time1 is None or time2 is None:
                raise ValueError("could not concatenate history output without time data")

            if sorted(obj1) != sorted(obj2):
                raise ValueError("could not concatenate history output with different data")
            
            if shift:
                obj2 = obj2.shift(time1[-1])
                mask2 = np.ones_like(time2, dtype=bool)

            else:
                if time1[0] > time2[0]:
                    obj1, obj2 = obj2, obj1
                    time1, time2 = time2, time1

                mask2 = time2 > time1[-1]

            output = HistoryOutput(
                {
                    key: np.concatenate((value, obj2[key][mask2]))
                    for key, value in obj1.to_dict(unit=True).items()
                }
            )

            for name in {"label", "type"}:
                value = getattr(obj1, name)

                if value and value == getattr(obj2, name):
                    setattr(output, name, value)

        elif isinstance(obj, (list, tuple)) and all(isinstance(x, HistoryOutput) for x in obj):
            output = self

            for x in obj:
                output = output.concatenate(x, shift)

        else:
            raise ValueError("could not concatenate with input obj")

        return output

    def plot(
        self,
        y: str,
        x: Optional[str] = None,
        ax: Optional[Axes] = None,
        logx: bool = False,
        logy: bool = False,
        xscale: Optional[float] = None,
        yscale: Optional[float] = None,
        time_unit: Optional[Literal["second", "hour", "day", "year"]] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Plot an history output.

        Parameters
        ----------
        y : str
            Data key for Y axis.
        x : str, optional
            Data key for X axis. Use time data by default.
        ax : matplotlib.axes.Axes, optional
            Plot axes.
        logx : bool, default False
            If True, use log scaling on X axis.
        logy : bool, default False
            If True, use log scaling on Y axis.
        xscale : scalar, optional
            Scaling factor applied to X axis.
        yscale : scalar, optional
            Scaling factor applied to Y axis.
        time_unit : {'second', 'hour', 'day', 'year'}, optional
            Unit of time axis (if *x* is time data).

        """
        ax = ax if ax is not None else plt.gca()
        xscale = xscale if xscale else 1.0
        yscale = yscale if yscale else 1.0
        time_unit = time_unit if time_unit else "second"

        if x:
            key, unit = self._get_key_unit(x)
            x = self[key]
            xlabel = f"{key} ({unit})" if unit else key

        else:
            x = self.time

            if x is None:
                raise ValueError("could not plot without time data")

            if time_unit == "second":
                pass

            elif time_unit == "hour":
                xscale = 1.0 / 3600.0

            elif time_unit == "day":
                xscale = 1.0 / 86400.0

            elif time_unit == "year":
                xscale = 1.0 / 31557600.0

            else:
                raise ValueError(f"invalid time unit '{time_unit}'")

            xlabel = f"Time ({time_unit})"
        
        try:
            unit = self.units[y]

        except KeyError:
            unit = None

        ylabel = f"{y} ({unit})" if unit else y
        ax.plot(x * xscale, self.data[y] * yscale, *args, **kwargs)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        if logx:
            ax.set_xscale("log")

        if logy:
            ax.set_yscale("log")

    def shift(self, t: float, inplace: bool = False) -> HistoryOutput | None:
        """
        Shift history output in time.

        Parameters
        ----------
        t : scalar
            Time value by which the time data will be shifted.
        inplace : bool, optional
            If True, update history output in-place.

        Returns
        -------
        toughio.HistoryOutput
            Shifted history output. Only provided if *inplace* is False.

        """
        obj = self if inplace else self.copy(deep=True)

        time = obj.time

        if time is None:
            raise ValueError("could not time shift without time data")

        time += t

        if not inplace:
            return obj

    def to_dataframe(self, unit: bool = True) -> pd.DataFrame | pd.Series:
        """
        Convert to a Pandas dataframe or series.

        Parameters
        ----------
        unit : bool, default True
            If True, add unit to column name.

        Returns
        -------
        pandas.DataFrame | pandas.Series
            Converted dataframe or series.

        """
        if self.ndim == 0:
            df = pd.Series(self.to_dict(unit=unit))

        else:
            df = pd.DataFrame(self.to_dict(unit=unit))
            time_key = self._get_time_key(unit=unit)

            if time_key:
                df.set_index(time_key, inplace=True)

        return df

    def to_dict(self, unit: bool = True) -> dict:
        """
        Convert to a dict.

        Parameters
        ----------
        unit : bool, default True
            If True, add unit to key.

        Returns
        -------
        dict
            Converted dict.

        """
        if unit:
            return {
                f"{key} ({unit if unit else '-'})": value
                for key, value, unit in self.items(unit=True)
            }

        else:
            return {key: value for key, value in self.items()}

    def _get_time_key(self, unit: bool = False) -> str | None:
        """Get key of time data."""
        time_key = None

        for key in self.keys():
            if key.upper().startswith("TIME"):
                time_key = key
                break

        if time_key:
            if unit:
                try:
                    time_unit = self.units[time_key]

                except KeyError:
                    time_unit = "S"
                    self.units[time_key] = time_unit

                time_key = f"{time_key} ({time_unit if time_unit else '-'})"

        return time_key

    @staticmethod
    def _get_key_unit(key: str) -> tuple[str, str]:
        """Split a key to (key, unit) pair."""
        match = re.match(r"^(.*?)(?:\(([^()]+)\))?$", key)

        if match:
            key, unit = match.groups()
            unit = unit if unit != "-" else None

        else:
            raise ValueError(f"invalid key '{key}'")

        key = key.strip() if key else None
        unit = unit.strip() if unit else None

        return key, unit

    @property
    def metadata(self) -> dict:
        """Return metadata."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict | None) -> None:
        """Set metadata."""
        value = value if value is not None else {}

        if not isinstance(value, dict):
            raise TypeError("metadata must be a dict")

        self._metadata = value

    @property
    def label(self) -> str | None:
        """Return label."""
        try:
            return self.metadata["label"]

        except KeyError:
            return None

    @label.setter
    def label(self, value: str) -> None:
        """Set label."""
        if value:
            self.metadata["label"] = value

    @property
    def type(self) -> str | None:
        """Return type."""
        try:
            return self.metadata["type"]

        except KeyError:
            return None

    @type.setter
    def type(self, value: str) -> None:
        if value:
            self.metadata["type"] = value

    @property
    def ndim(self) -> int:
        """Return data dimension."""
        return (
            np.ndim(self[list(self.keys())[0]])
            if len(self)
            else None
        )

    @property
    def size(self) -> int:
        """Return data size."""
        return (
            len(self[list(self.keys())[0]])
            if self.ndim == 1
            else 1
            if self.ndim == 0
            else None
        )

    @property
    def time(self) -> ArrayLike | None:
        """Return time data."""
        time_key = self._get_time_key()

        return self[time_key] if time_key else None

    @property
    def units(self) -> dict:
        """Return data units."""
        if "units" not in self.metadata:
            self.metadata["units"] = {}

        return self.metadata["units"]
