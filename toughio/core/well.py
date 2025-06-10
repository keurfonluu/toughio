from __future__ import annotations

from typing import Literal, Optional

import numpy as np
import pandas as pd
import pvgridder as pvg
import pyvista as pv
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from .history_output import HistoryOutput


class Pipe:
    """Pipe class."""

    __name__: str = "Pipe"
    __qualname__: str = "toughio.Pipe"

    def __init__(
        self,
        radius: float,
        zmin: float,
        zmax: float,
        material: str,
        thickness: float = 0.0,
    ) -> None:
        """Initialize a pipe."""
        self.radius = radius
        self.zmin = zmin
        self.zmax = zmax
        self.material = material
        self.thickness = thickness

        if self.is_porous and material.upper().startswith(("W", "X")):
            raise ValueError("could not create porous well section with material name starting with 'W' or 'X")

        elif not self.is_porous and not material.upper().startswith(("W", "X")):
            raise ValueError("could not create well section with material name not starting with 'W' or 'X")

    def to_pyvista(self, resolution: int = 64) -> pv.PolyData:
        """
        Convert pipe to a PyVista mesh.

        Parameters
        ----------
        resolution : int, default 64
            Number of points on the circular face of the cylinder.

        Returns
        -------
        pyvista.PolyData
            Output mesh.

        """
        center = [0.0, 0.0, 0.5 * (self.zmin + self.zmax)]
        pipe = (
            pvg.CylindricalShell(self.radius, self.radius + self.thickness, self.length, 1, resolution, center=center).cast_to_unstructured_grid().clean(1.0e-8)
            if self.is_porous
            else pv.Cylinder(center, [0.0, 0.0, -1.0], self.radius, self.length, resolution, capping=False)
        )
        pipe.cell_data["Material"] = np.array([self.material] * resolution, dtype="<U5")

        return pipe

    @property
    def is_porous(self) -> bool:
        """Return True if pipe is treated as a porous medium."""
        return self.thickness > 0.0

    @property
    def length(self) -> float:
        """Return pipe's length."""
        return self.zmax - self.zmin

    @property
    def material(self) -> str:
        """Return pipe's material."""
        return self._material

    @material.setter
    def material(self, value: str) -> None:
        """Set pipe's material."""
        self._material = value

    @property
    def radius(self) -> float:
        """Return pipe's radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        """Set pipe's radius."""
        self._radius = value

    @property
    def thickness(self) -> float:
        """Return pipe's thickness."""
        return self._thickness

    @thickness.setter
    def thickness(self, value: float) -> None:
        """Set pipe's thickness."""
        self._thickness = value

    @property
    def zmin(self) -> float:
        """Return pipe's bottom depth."""
        return self._zmin

    @zmin.setter
    def zmin(self, value: float) -> None:
        """Set pipe's bottom depth."""
        self._zmin = value

    @property
    def zmax(self) -> float:
        """Return pipe's top depth."""
        return self._zmax

    @zmax.setter
    def zmax(self, value: float) -> None:
        """Set pipe's top depth."""
        self._zmax = value


class WellCasing:
    """
    Well casing class.

    """

    __name__: str = "WellCasing"
    __qualname__: str = "toughio.WellCasing"

    def __init__(self) -> None:
        """Initialize a well casing."""
        self._pipes = []
        self._metadata = {"Wellheads": [], "Connections": []}
        
    def add_pipe(
        self,
        radius: float,
        zmin: float,
        zmax: float,
        material: str,
        thickness: float = 0.0,
    ) -> Pipe:
        """
        Add a pipe section.

        Parameters
        ----------
        radius : float
            Radius.
        zmin : float
            Bottom depth.
        zmax : float
            Top depth.
        material : str
            Material.
        thickness : float, default 0.0
            Thickness. If non-zero, pipe is treated as a porous medium.

        Returns
        -------
        toughio.Pipe
            Pipe section.

        """
        pipe = Pipe(radius, zmin, zmax, material, thickness)

        if self.pipes:
            if self.pipes[-1].radius > radius:
                raise ValueError()

        self.pipes.append(pipe)

        return pipe

    def set_connection(
        self,
        type_: Literal["backward", "branch", "forward", "gas", "heat", "liquid", "none", "perforation"],
        pipe1: Pipe,
        pipe2: Optional[Pipe] = None,
        zmin: Optional[float] = None,
        zmax: Optional[float] = None,
    ) -> None:
        """
        Set a well-well or well-formation connection.

        Parameters
        ----------
        type_ : {'backward', 'branch', 'forward', 'gas', 'heat', 'liquid', 'none', 'perforation'}
            Connection type.
        pipe1 : toughio.Pipe
            Starting pipe.
        pipe2 : toughio.Pipe, optional
            Ending pipe for well-well connection. If None, define a well-formation
            connection.
        zmin : float, optional
            Lower depth interval.
        zmax : float, optional
            Upper depth interval.

        """
        if (
            pipe1 not in self.pipes
            or (pipe2 is not None and pipe2 not in self.pipes)
        ):
            raise ValueError("could not define connection with pipes not in the casing")

        elif type_ == "perforation" and pipe2 is not None:
            raise ValueError("could not define a perforation connection with an end pipe")

        if pipe2 is not None:
            if type_ not in {"branch", "forward", "backward", "none"}:
                raise ValueError(f"invalid well-well connection type '{type_}'")

            if pipe1.zmin > pipe2.zmax or pipe2.zmin > pipe1.zmax:
                raise ValueError("start and end pipes are not connected")

            zmin = zmin if zmin is not None else max(pipe1.zmin, pipe2.zmin)
            zmax = zmax if zmax is not None else min(pipe1.zmax, pipe2.zmax)

        else:
            if type_ not in {"heat", "perforation", "gas", "liquid", "backward", "none"}:
                raise ValueError(f"invalid well-formation connection type '{type_}'")

            zmin = zmin if zmin else pipe1.zmin
            zmax = zmax if zmax else pipe1.zmax

        connection = {
            "type": type_,
            "pipe1": pipe1,
            "pipe2": pipe2,
            "zmin": zmin,
            "zmax": zmax,
        }
        self.connections.append(connection)

    def set_wellhead(self, pipe: Pipe) -> None:
        """
        Set pipe section as wellhead.

        Parameters
        ----------
        pipe : toughio.Pipe
            Wellhead pipe section.

        """
        if pipe not in self.pipes:
            raise ValueError("could not set wellhead to a pipe not in the casing")

        if pipe.is_porous:
            raise ValueError("could not set wellhead to a porous section")

        self.wellheads.append(pipe)

    def to_pyvista(
        self,
        resolution: int = 64,
        well_only: bool = False,
    ) -> pv.PolyData:
        """
        Convert well to a PyVista mesh.

        Returns
        -------
        pyvista.PolyData
            Output mesh.

        """
        pipes = [
            pipe.to_pyvista(resolution)
            for pipe in self.pipes
            if not (well_only and pipe.is_porous)
        ]

        return pv.merge(pipes)

    def plot(
        self,
        well_only: bool = False,
        xscale: Optional[float] = None,
        zscale: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Plot a well.

        Parameters
        ----------
        well_only : bool, default False
            If True, only plot non-porous pipe sections.
        xscale : float, optional
            Scaling in the X direction.
        zscale : float, optional
            Scaling in the Z direction.
        **kwargs : dict, optional
            Additional keyword arguments. See ``pyvista.Plotter`` for more details.

        """
        mesh = self.to_pyvista(well_only=well_only)

        p = pv.Plotter(**kwargs)
        
        if xscale or zscale:
            p.set_scale(xscale=xscale, zscale=zscale)

        p.add_mesh(
            mesh,
            scalars="Material",
            opacity=0.5,
        )
        p.add_axes()
        p.show()

    @property
    def connections(self) -> list[dict]:
        """Return well connections."""
        return self.metadata["Connections"]

    @property
    def materials(self) -> ArrayLike:
        """Return well materials."""
        return np.array([pipe.material for pipe in self.pipes])

    @property
    def metadata(self) -> dict:
        """Return well metadata."""
        return self._metadata

    @property
    def pipes(self) -> list[Pipe]:
        """Return pipe sections."""
        return self._pipes

    @property
    def radii(self) -> ArrayLike:
        """Return well radii."""
        return np.array([pipe.radius for pipe in self.pipes])

    @property
    def wellheads(self) -> int:
        """Return wellheads."""
        return self.metadata["Wellheads"]


class WellOutput(HistoryOutput):
    """
    Well output class.

    Parameters
    ----------
    obj : dict, optional
        Data dict.
    metadata : dict, optional
        Output metadata.

    """

    __name__: str = "WellOutput"
    __qualname__: str = "toughio.WellOutput"

    def __init__(
        self,
        obj: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Initialize a well output."""
        super().__init__(obj, metadata)

    def __call__(self, t: Optional[ArrayLike] = None, z: Optional[ArrayLike] = None) -> WellOutput:
        """Interpolate a well output."""
        from scipy.interpolate import griddata

        if t is None and z is None:
            raise ValueError("could not interpolate well output without time or depth data")

        t = t if t is not None else self.time
        z = z if z is not None else self.depth
        T, Z = np.meshgrid(t, z)

        tp = self.data["Time"]
        zp = self.data["Depth"]

        out = {
            key: griddata(
                (tp, zp),
                value,
                (T, Z),
                method="linear",
            ).ravel()
            for key, value in self.to_dict().items()
        }
        out = WellOutput(out)

        # Make sure time and depth arrays are unique
        if np.ndim(t) == 0:
            out.data["Time"][:] = t

        if np.ndim(z) == 0:
            out.data["Depth"][:] = z

        return out

    def _get_time_key(self, *args, **kwargs) -> str:
        """Get key of time data."""
        return "Time"

    def plot(
        self,
        key: str,
        ax: Optional[Axes] = None,
        logx: bool = False,
        logy: bool = False,
        *args,
        **kwargs,
    ) -> None:
        """
        Plot a well output.

        Parameters
        ----------
        key : str
            Data key to plot.
        ax : matplotlib.axes.Axes, optional
            Plot axes.
        logx : bool, default False
            If True, use log scaling on X axis.
        logy : bool, default False
            If True, use log scaling on Y axis.
        *args
            Additional arguments to pass to the plot function.
        **kwargs
            Additional keyword arguments to pass to the plot function.
        
        """
        ax = ax if ax is not None else plt.gca()
        t = self.time
        z = self.depth

        if t.size == 1:
            ax.plot(self.data[key], z, *args, **kwargs)
            ax.set_xlabel(key)
            ax.set_ylabel("Depth")
            ax.yaxis.set_inverted(True)

        elif z.size == 1:
            ax.plot(t, self.data[key], *args, **kwargs)
            ax.set_xlabel("Time")
            ax.set_ylabel(key)

        else:
            data = (
                self(0.5 * (t[:-1] + t[1:]), 0.5 * (z[:-1] + z[1:]))
                .data[key]
                .reshape((z.size - 1, t.size - 1))
            )
            ax.pcolormesh(t, z, data, *args, **kwargs)
            ax.yaxis.set_inverted(True)
            ax.set_xlabel("Time")
            ax.set_ylabel("Depth")
            
        if logx:
            ax.set_xscale("log")

        if logy:
            ax.set_yscale("log")

    def to_dataframe(self, *args, **kwargs) -> pd.DataFrame | pd.Series:
        """
        Convert to a Pandas dataframe or series.

        Returns
        -------
        pandas.DataFrame | pandas.Series
            Converted dataframe or series.

        """
        return super().to_dataframe(unit=False)

    def to_dict(self, *args, **kwargs) -> dict:
        """
        Convert to a dict.

        Returns
        -------
        dict
            Converted dict.

        """
        return super().to_dict(unit=False)

    @property
    def depth(self) -> ArrayLike:
        """Return depth data."""
        return np.unique(self.data["Depth"])

    @property
    def time(self) -> ArrayLike | None:
        """Return time data."""
        time_key = self._get_time_key()

        return np.unique(self[time_key]) if time_key else None
