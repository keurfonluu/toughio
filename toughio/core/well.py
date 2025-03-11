from __future__ import annotations
from typing import Optional
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
    def __init__(self) -> None:
        self._pipes = []
        self._branches = []
        
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

    def add_branch(self, pipe1: Pipe, pipe2: Pipe, z: Optional[float] = None) -> None:
        self.branches.append((pipe1.id, pipe2.id, z))

    def to_pyvista(self, resolution: int = 64, well_only: bool = False) -> pv.PolyData | pv.UnstructuredGrid:
        pipes = [pipe.to_pyvista(resolution) for pipe in self.pipes if not (well_only and pipe.is_porous)]

        return pv.merge(pipes)

    def plot(self, zscale: Optional[float] = None, **kwargs) -> None:
        mesh = self.to_pyvista()
        if zscale:
            mesh.points[:, 2] *= zscale

        mesh.plot(scalars="Material", opacity=0.5, **kwargs)

    @property
    def branches(self) -> list:
        return self._branches

    @property
    def pipes(self) -> list[Pipe]:
        return self._pipes

    @property
    def radii(self) -> ArrayLike:
        return np.array([pipe.radius for pipe in self.pipes])

    @property
    def materials(self) -> ArrayLike:
        return np.array([pipe.material for pipe in self.pipes])
