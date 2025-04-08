from __future__ import annotations
from typing import Literal, Optional
from numpy.typing import ArrayLike

import numpy as np
import pyvista as pv
import pvgridder as pvg


class Pipe:
    def __init__(
        self,
        radius: float,
        zmin: float,
        zmax: float,
        material: str,
        thickness: float = 0.0,
        id_: Optional[int] = None,
    ) -> None:
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
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def is_porous(self) -> bool:
        return self.thickness > 0.0

    @property
    def length(self) -> float:
        return self.zmax - self.zmin

    @property
    def material(self) -> str:
        return self._material

    @material.setter
    def material(self, value: str) -> None:
        self._material = value

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value

    @property
    def thickness(self) -> float:
        return self._thickness

    @thickness.setter
    def thickness(self, value: float) -> None:
        self._thickness = value

    @property
    def zmin(self) -> float:
        return self._zmin

    @zmin.setter
    def zmin(self, value: float) -> None:
        self._zmin = value

    @property
    def zmax(self) -> float:
        return self._zmax

    @zmax.setter
    def zmax(self, value: float) -> None:
        self._zmax = value


class WellCasing:
    def __init__(
        self,

    ) -> None:
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
        pipe = Pipe(radius, zmin, zmax, material, thickness, id_=len(self.pipes))

        if self.pipes:
            if self.pipes[-1].radius > radius:
                raise ValueError()

        self.pipes.append(pipe)

        return pipe

    def set_connection(
        self,
        type_: Literal["backward", "branch", "forward", "gas", "heat", "liquid", "perforation"],
        pipe1: Pipe,
        pipe2: Optional[Pipe] = None,
        zmin: Optional[float] = None,
        zmax: Optional[float] = None,
    ) -> None:
        if (
            pipe1 not in self.pipes
            or (pipe2 is not None and pipe2 not in self.pipes)
        ):
            raise ValueError("could not define connection with pipes not in the casing")

        elif type_ == "perforation" and pipe2 is not None:
            raise ValueError("could not define a perforation connection with an end pipe")

        if pipe2 is not None:
            if type_ not in {"branch", "heat", "forward", "backward"}:
                raise ValueError(f"invalid well-well connection type '{type_}'")

            if pipe1.zmin > pipe2.zmax or pipe2.zmin > pipe1.zmax:
                raise ValueError("start and end pipes are not connected")

            zmin = zmin if zmin is not None else max(pipe1.zmin, pipe2.zmin)
            zmax = zmax if zmax is not None else min(pipe1.zmax, pipe2.zmax)

        else:
            if type_ not in {"heat", "perforation", "gas", "liquid", "backward"}:
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
        if pipe not in self.pipes:
            raise ValueError("could not set wellhead to a pipe not in the casing")

        if pipe.is_porous:
            raise ValueError("could not set wellhead to a porous section")

        self.wellheads.append(pipe)

    def to_pyvista(self, resolution: int = 64, well_only: bool = False) -> pv.PolyData | pv.UnstructuredGrid:
        pipes = [pipe.to_pyvista(resolution) for pipe in self.pipes if not (well_only and pipe.is_porous)]

        return pv.merge(pipes)

    def plot(
        self,
        well_only: bool = False,
        xscale: Optional[float] = None,
        zscale: Optional[float] = None,
        **kwargs
    ) -> None:
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
        return self.metadata["Connections"]

    @property
    def materials(self) -> ArrayLike:
        return np.array([pipe.material for pipe in self.pipes])

    @property
    def metadata(self) -> dict:
        return self._metadata

    @property
    def pipes(self) -> list[Pipe]:
        return self._pipes

    @property
    def radii(self) -> ArrayLike:
        return np.array([pipe.radius for pipe in self.pipes])

    @property
    def wellheads(self) -> int:
        return self.metadata["Wellheads"]
