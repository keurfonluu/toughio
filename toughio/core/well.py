from __future__ import annotations
from typing import Literal, Optional
from numpy.typing import ArrayLike

import numpy as np
import pyvista as pv
import pvgridder as pvg


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
        id_: Optional[int] = None,
    ) -> None:
        """Initialize a pipe."""
        self.radius = radius
        self.zmin = zmin
        self.zmax = zmax
        self.material = material
        self.thickness = thickness
        self.id = id_

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
    def id(self) -> int:
        """Return pipe ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Set pipe ID."""
        self._id = value

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
        pipe = Pipe(radius, zmin, zmax, material, thickness, id_=len(self.pipes))

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
