from __future__ import annotations

import os
from collections.abc import Sequence
from typing import TYPE_CHECKING, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvgridder as pvg
import pyvista as pv
from matplotlib.axes import Axes
from typing_extensions import Self

from .history_output import HistoryOutput


if TYPE_CHECKING:
    from typing import Literal, Optional

    from numpy.typing import ArrayLike, NDArray

    import toughio


class Pipe:
    """
    Class representing a section of a wellbore.

    Parameters
    ----------
    points : ArrayLike
        3D coordinates of the polyline representing the pipe section.
    material : str
        The material of the pipe section.
    inner_radius : float
        The inner radius of the pipe section.
    thickness : float, default 0.0
        The thickness of the pipe section. If non-zero, the pipe is treated as a porous
        medium.
    other_data : dict, optional
        Additional cell data to be stored in the pipe.

    """

    __name__: str = "Pipe"
    __qualname__: str = "toughio.Pipe"

    def __init__(
        self,
        points: ArrayLike,
        material: str,
        inner_radius: float,
        thickness: float = 0.0,
        other_data: Optional[dict] = None,
    ) -> None:
        """Initialize a pipe section."""
        points = np.asanyarray(points)
        other_data = other_data if other_data is not None else {}

        pipe = pv.MultipleLines(points)
        pipe.clear_data()
        pipe.cell_data["Material"] = np.atleast_1d(material)
        pipe.cell_data["Radius"] = np.atleast_1d(inner_radius)
        pipe.cell_data["Thickness"] = np.atleast_1d(thickness)
        self._pyvista = cast(pv.PolyData, pipe)

        if self.is_porous and material.upper().startswith(("W", "X")):
            raise ValueError(
                "could not create porous well section with material name starting with 'W' or 'X"
            )

        elif not self.is_porous and not material.upper().startswith(("W", "X")):
            raise ValueError(
                "could not create well section with material name not starting with 'W' or 'X"
            )

        for k, v in other_data.items():
            pipe.cell_data[k] = v

    @property
    def initial_conditions(self) -> NDArray | None:
        """Return the initial conditions of the pipe section."""
        return (
            self.pyvista.cell_data["Initial Conditions"].squeeze()
            if "Initial Conditions" in self.pyvista.cell_data
            else None
        )

    @initial_conditions.setter
    def initial_conditions(self, value: ArrayLike) -> None:
        """Set the initial conditions of the pipe section."""
        value = np.asanyarray(value)

        if value.ndim != 1:
            raise ValueError("could not add initial conditions with invalid shape")

        self.pyvista.cell_data["Initial Conditions"] = np.atleast_2d(value)

    @property
    def inner_radius(self) -> float:
        """Return the inner radius of the pipe section."""
        return self.pyvista.cell_data["Radius"][0]

    @inner_radius.setter
    def inner_radius(self, value: float) -> None:
        """Set the inner radius of the pipe section."""
        self.pyvista.cell_data["Radius"] = np.asanyarray(value)

    @property
    def is_porous(self) -> bool:
        """Return whether the pipe section is treated as a porous medium."""
        return self.thickness > 0.0

    @property
    def length(self) -> float:
        """Return the length of the pipe section."""
        return np.linalg.norm(np.diff(self.points, axis=0), axis=1).sum()

    @property
    def material(self) -> str:
        """Return the material of the pipe section."""
        return self.pyvista.cell_data["Material"][0]

    @material.setter
    def material(self, value: str) -> None:
        """Set the material of the pipe section."""
        self.pyvista.cell_data["Material"] = value

    @property
    def points(self) -> NDArray:
        """Return the 3D coordinates of the pipe section."""
        return self.pyvista.points

    @property
    def pyvista(self) -> pv.PolyData:
        """Return the underlying PyVista mesh for the pipe section."""
        return self._pyvista

    @property
    def thickness(self) -> float:
        """Return the thickness of the pipe section."""
        return self.pyvista.cell_data["Thickness"][0]

    @thickness.setter
    def thickness(self, value: float) -> None:
        """Set the thickness of the pipe section."""
        self.pyvista.cell_data["Thickness"] = np.asanyarray(value)

    @property
    def zmin(self) -> float:
        """Return the bottom depth (minimum z) of the pipe section."""
        return self.points[:, 2].min()

    @property
    def zmax(self) -> float:
        """Return the top depth (maximum z) of the pipe section."""
        return self.points[:, 2].max()


class WellCasing:
    """Class representing a well casing."""

    __name__: str = "WellCasing"
    __qualname__: str = "toughio.WellCasing"

    def __init__(self) -> None:
        """Initialize a well casing."""
        self._pipes = []
        self._metadata = {"Wellheads": [], "Connections": []}

    def add_pipe(
        self,
        material: str,
        inner_radius: float,
        zmin: float,
        zmax: float,
        thickness: float = 0.0,
    ) -> Pipe:
        """
        Add a pipe section.

        Parameters
        ----------
        material : str
            The material of the pipe section.
        inner_radius : float
            The inner radius of the pipe section.
        zmin : float
            The bottom depth of the pipe section.
        zmax : float
            The top depth of the pipe section.
        thickness : float, default 0.0
            The thickness of the pipe section. If non-zero, pipe is treated as a porous
            medium.

        Returns
        -------
        toughio.Pipe
            Pipe section.

        """
        points = [
            [0.0, 0.0, zmin],
            [0.0, 0.0, zmax],
        ]
        pipe = Pipe(points, material, inner_radius, thickness)

        if self.pipes:
            if self.pipes[-1].inner_radius > inner_radius:
                raise ValueError(
                    f"could not add pipe with smaller inner radius than {self.pipes[-1].inner_radius}"
                )

        self.pipes.append(pipe)

        return pipe

    def set_connection(
        self,
        type_: Literal[
            "backward",
            "branch",
            "forward",
            "gas",
            "heat",
            "liquid",
            "none",
            "perforation",
        ],
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
            The type of connection.
        pipe1 : toughio.Pipe
            The starting pipe for the connection.
        pipe2 : toughio.Pipe, optional
            The ending pipe for well-well connection. If None, define a well-formation
            connection.
        zmin : float, optional
            The lower depth interval.
        zmax : float, optional
            The upper depth interval.

        """
        if pipe1 not in self.pipes or (pipe2 is not None and pipe2 not in self.pipes):
            raise ValueError("could not define connection with pipes not in the casing")

        elif type_ == "perforation" and pipe2 is not None:
            raise ValueError(
                "could not define a perforation connection with an end pipe"
            )

        if pipe2 is not None:
            if type_ not in {"branch", "forward", "backward", "none"}:
                raise ValueError(f"invalid well-well connection type '{type_}'")

            if pipe1.zmin > pipe2.zmax or pipe2.zmin > pipe1.zmax:
                raise ValueError("start and end pipes are not connected")

            zmin = zmin if zmin is not None else max(pipe1.zmin, pipe2.zmin)
            zmax = zmax if zmax is not None else min(pipe1.zmax, pipe2.zmax)

        else:
            if type_ not in {
                "heat",
                "perforation",
                "gas",
                "liquid",
                "backward",
                "none",
            }:
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
            The pipe section to set as wellhead.

        """
        if pipe not in self.pipes:
            raise ValueError("could not set wellhead to a pipe not in the casing")

        if pipe.is_porous:
            raise ValueError("could not set wellhead to a porous section")

        self.wellheads.append(pipe)

    def to_pyvista(
        self,
        well_only: bool = False,
    ) -> pv.PolyData:
        """
        Return the PyVista representation of the well casing.

        Parameters
        ----------
        well_only : bool, default False
            If True, only include well sections (i.e., non-porous).

        Returns
        -------
        pyvista.PolyData
            The PyVista mesh representation of the well casing.

        """
        pipes = []

        for pipe in self.pipes:
            if well_only and pipe.is_porous:
                continue

            center = [0.0, 0.0, 0.5 * (pipe.zmin + pipe.zmax)]
            pipe_ = (
                pvg.CylindricalShell(
                    pipe.inner_radius,
                    pipe.inner_radius + pipe.thickness,
                    pipe.length,
                    r_resolution=1,
                    theta_resolution=64,
                    center=center,
                )
                .cast_to_unstructured_grid()
                .clean(tolerance=1.0e-8)  # type: ignore
                if pipe.is_porous
                else pv.Cylinder(
                    center=center,
                    direction=[0.0, 0.0, -1.0],
                    radius=pipe.inner_radius,
                    height=pipe.length,
                    resolution=64,
                    capping=False,
                )
            )
            pipe_.clear_data()
            pipe_.cell_data["Material"] = [pipe.material] * 64
            pipes.append(pipe_)

        return pv.merge(pipes)

    def plot(
        self,
        plotter: Optional[pv.Plotter] = None,
        well_only: bool = False,
        **kwargs,
    ) -> None:
        """
        Plot the well casing.

        Parameters
        ----------
        plotter : Optional[pyvista.Plotter], optional
            Active plotter.
        well_only : bool, default False
            If True, only plot non-porous pipe sections.
        **kwargs
            Additional keyword arguments. See ``pyvista.Plotter`` for more details.

        """
        mesh = self.to_pyvista(well_only=well_only)

        if plotter is None:
            p = pv.Plotter(**kwargs)

        else:
            p = plotter

        p.add_mesh(
            mesh,
            scalars="Material",
            opacity=0.5,
        )
        p.add_axes()  # type: ignore

        if plotter is None:
            p.show()

    @property
    def connections(self) -> list[dict]:
        """Return well connections."""
        return self.metadata["Connections"]

    @property
    def materials(self) -> NDArray:
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
    def radii(self) -> NDArray:
        """Return well radii."""
        return np.array([pipe.inner_radius for pipe in self.pipes])

    @property
    def wellheads(self) -> list[Pipe]:
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

    def __call__(
        self, t: Optional[ArrayLike] = None, z: Optional[ArrayLike] = None
    ) -> WellOutput:
        """Interpolate a well output."""
        from scipy.interpolate import griddata

        if t is None and z is None:
            raise ValueError(
                "could not interpolate well output without time or depth data"
            )

        t = t if t is not None else self.time
        z = z if z is not None else self.depth

        if t is None:
            raise ValueError("could not interpolate well output without time data")

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

        if t is None:
            raise ValueError("could not plot well output without time data")

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
    def depth(self) -> NDArray:
        """Return depth data."""
        return np.unique(self.data["Depth"])

    @property
    def time(self) -> NDArray | None:
        """Return time data."""
        time_key = self._get_time_key()

        return np.unique(self[time_key]) if time_key else None


class WellTrajectory:
    """
    Class representing the trajectory of a well.

    Parameters
    ----------
    arg : str | PathLike | ArrayLike | pyvista.PolyData
        Initialize a new well trajectory instance:

         - From a file
         - From a polyline
         - From an array representing the origin point (usually the bottom of the wellhead)

    wellhead_material : str
        The material of the wellhead. Only used if *arg* is an array.
    wellhead_inner_radius : float
        The inner radius of the wellhead. Only used if *arg* is an array.
    wellhead_height : float, default 1.0
        The height of the wellhead. Only used if *arg* is an array.
    initial_direction : ArrayLike, optional
        The initial direction of the well trajectory (usually pointing downward). Only
        used if *arg* is an array.

    """

    __name__: str = "WellTrajectory"
    __qualname__: str = "toughio.WellTrajectory"

    def __init__(
        self,
        arg: str | os.PathLike | ArrayLike | pv.DataObject | pv.PolyData,
        wellhead_material: Optional[str] = None,
        wellhead_inner_radius: Optional[float] = None,
        wellhead_height: float = 1.0,
        initial_direction: Optional[ArrayLike] = None,
    ) -> None:
        """Initialize the well trajectory."""
        if isinstance(arg, (str, os.PathLike)):
            arg = pv.read(str(arg))

        if isinstance(arg, (pv.DataObject, pv.DataSet)):
            if (
                isinstance(arg, pv.PolyData)
                and arg.user_dict.get("toughioType") == "WellTrajectory"
            ):
                self._pipes = [
                    Pipe(
                        points=line.points,
                        material=line.cell_data["Material"][0],
                        inner_radius=line.cell_data["Radius"][0],
                        thickness=line.cell_data["Thickness"][0],
                        other_data={
                            k: v
                            for k, v in line.cell_data.items()
                            if k not in {"Material", "Radius", "Thickness"}
                        },
                    )
                    for line in pvg.split_lines(arg, as_lines=False)
                ]
                self.direction = arg.user_dict.get(
                    "DirectionVector",
                    self.points[-1] - self.points[-2],
                )

            else:
                raise TypeError("could not initialize well trajectory")

        elif isinstance(arg, (list, tuple, np.ndarray)) and np.ndim(arg) == 1:
            origin = np.asanyarray(arg)

            if wellhead_material is None or wellhead_inner_radius is None:
                raise ValueError(
                    "could not initialize well trajectory from an origin points without wellhead material and inner radius"
                )

            self.direction = (
                (0.0, 0.0, -1.0) if initial_direction is None else initial_direction
            )
            self._pipes = [
                Pipe(
                    points=[
                        origin - wellhead_height * self.direction,
                        origin,
                    ],
                    material=wellhead_material,
                    inner_radius=wellhead_inner_radius,
                )
            ]

        else:
            raise ValueError("could not initialize well trajectory")

    def add_pipe(
        self,
        material: str,
        inner_radius: float,
        length: float,
        resolution: int = 1,
        end_direction: Optional[ArrayLike] = None,
        curved: bool = False,
    ) -> Pipe:
        """
        Add a pipe to the well trajectory.

        Parameters
        ----------
        material : str
            The material of the pipe.
        inner_radius : float
            The inner radius of the pipe.
        length : float
            The length of the pipe.
        resolution : int, optional
            The resolution along the pipe (i.e., discretization).
        end_direction : ArrayLike, optional
            The end direction of the pipe.
        curved : bool, default False
            If True, incrementally deviate the pipe until end direction is reached.

        Returns
        -------
        toughio.Pipe
            The added pipe.

        """
        origin = self.points[-1]
        end_direction = end_direction if end_direction is not None else self.direction

        points = (
            pvg.CurvedLine(
                origin=origin,
                length=length,
                start=self.direction,
                end=end_direction,
                resolution=resolution,
            )
            if curved
            else pvg.CurvedLine(
                origin=origin,
                length=length,
                start=end_direction,
                resolution=resolution,
            )
        ).points
        self.direction = end_direction
        self.pipes.append(
            Pipe(
                points=points,
                material=material,
                inner_radius=inner_radius,
            )
        )

        return self.pipes[-1]

    def intersect(
        self,
        mesh: pv.DataSet | toughio.Mesh,
        min_length: float = 1.0e-4,
        tolerance: float = 1.0e-8,
    ) -> Self:
        """
        Intersect the well trajectory with a mesh.

        Parameters
        ----------
        mesh : pyvista.DataSet | toughio.Mesh
            The mesh to intersect with.
        min_length : float, default 1.0e-4
            The minimum length of an intersection.
        tolerance : float, default 1.0e-8
            The absolute tolerance to use to find cells along the trajectory.

        Returns
        -------
        toughio.WellTrajectory
            The intersected well trajectory.

        """
        from .. import CylindricMesh, Mesh

        if isinstance(mesh, CylindricMesh):
            raise ValueError(
                "could not intersect a well trajectory with a cylindric mesh"
            )

        elif isinstance(mesh, Mesh):
            mesh_ = mesh.pyvista

        else:
            mesh_ = mesh

        intersection = pvg.intersect_polyline(
            mesh_,  # type: ignore
            line=self.to_pyvista(as_lines=True),
            min_length=min_length,
            tolerance=tolerance,
            pass_cell_data=True,
            ignore_points_before_entry=False,
            ignore_points_after_exit=True,
        )
        intersection.user_dict["toughioType"] = "WellTrajectory"

        return self.__class__(intersection)

    def plot(
        self, plotter: Optional[pv.Plotter] = None, show_points: bool = True, **kwargs
    ) -> None:
        """
        Plot the well trajectory.

        Parameters
        ----------
        plotter : Optional[pyvista.Plotter], optional
            Active plotter.
        show_points : bool, default True
            Whether to show the points along the well trajectory.
        **kwargs
            Additional keyword arguments. See ``pyvista.Plotter`` for more details.

        """
        mesh = self.to_pyvista()

        if plotter is None:
            p = pv.Plotter(**kwargs)

        else:
            p = plotter

        p.add_mesh(
            mesh,
            color="black",
            line_width=5,
            render_lines_as_tubes=True,
        )

        if show_points:
            p.add_mesh(
                pv.PolyData(mesh.points),
                color="red",
                point_size=5,
                render_points_as_spheres=True,
            )

        p.add_axes()  # type: ignore

        if plotter is None:
            p.show()

    def shift(self, vector: Sequence[float]) -> Self:
        """
        Shift the well trajectory by a given vector.

        Parameters
        ----------
        vector : Sequence[float]
            The vector by which to shift the well trajectory.

        Returns
        -------
        toughio.WellTrajectory
            The shifted well trajectory.

        """
        return self.__class__(self.to_pyvista().translate(vector))

    def write(self, filename: str | os.PathLike) -> None:
        """
        Write the well trajectory to a file.

        Parameters
        ----------
        filename : str | PathLike
            The output file name.

        """
        self.to_pyvista().save(filename)

    save = write  # Alias to avoid confusion

    def to_pyvista(
        self,
        as_lines: bool = False,
    ) -> pv.PolyData:
        """
        Return the PyVista representation of the well trajectory.

        Parameters
        ----------
        as_lines : bool, default False
            If True, return the well trajectory as multiple lines.

        Returns
        -------
        pyvista.PolyData
            The PyVista representation of the well trajectory.

        """
        mesh = pvg.merge_lines(
            [pipe.pyvista for pipe in self.pipes],
            as_lines=as_lines,
        )
        mesh.user_dict["toughioType"] = "WellTrajectory"
        mesh.user_dict["DirectionVector"] = self.direction.tolist()

        return mesh

    @property
    def centers(self) -> NDArray:
        """Return the centers of the pipes along the well trajectory."""
        points = self.points

        return 0.5 * (points[:-1] + points[1:])

    @property
    def direction(self) -> NDArray:
        """Return the end direction of the well trajectory."""
        return self._direction

    @direction.setter
    def direction(self, value: ArrayLike) -> None:
        """Set the end direction of the well trajectory."""
        self._direction = np.atleast_1d(value) / np.linalg.norm(value)

    @property
    def initial_conditions(self) -> NDArray | None:
        """Return initial conditions along the well trajectory."""
        initial_conditions = [
            pipe.initial_conditions if pipe.initial_conditions is not None else []
            for pipe in self.pipes
        ]

        # Pad with NaNs to make sure all arrays have the same length
        max_length = max(len(ic) for ic in initial_conditions)
        initial_conditions = np.hstack(
            [
                np.pad(ic, (0, max_length - len(ic)), constant_values=np.nan)
                for ic in initial_conditions
            ]
        )

        return initial_conditions if not np.isnan(initial_conditions).all() else None

    @initial_conditions.setter
    def initial_conditions(self, value: ArrayLike) -> None:
        """Set initial conditions along the well trajectory."""
        value = np.asanyarray(value)

        if value.ndim != 2:
            raise ValueError("could not set initial conditions with invalid shape")

        if value.shape[0] != self.size:
            raise ValueError(
                "could not set initial conditions with mismatched number of pipe sections"
            )

        for pipe, value_ in zip(self.pipes, value):
            pipe.initial_conditions = value_

    @property
    def intersected_cell_ids(self) -> ArrayLike | None:
        """Return intersected cell IDs."""
        mesh = self.to_pyvista()
        ids = mesh.cell_data.get("IntersectedCellIds")

        return ids[ids >= 0] if ids is not None else None

    @property
    def length(self) -> float:
        """Return the length of the well trajectory."""
        return (np.linalg.norm(np.diff(self.points, axis=0), axis=1)).sum()

    @property
    def materials(self) -> NDArray:
        """Return the materials along the well trajectory."""
        return np.array([pipe.material for pipe in self.pipes])

    @property
    def n_cells(self) -> int:
        """Return the number of cells along the well trajectory."""
        return self.size

    @property
    def pipes(self) -> list[Pipe]:
        """Return the pipes along the well trajectory."""
        return self._pipes

    @property
    def points(self) -> NDArray:
        """Return the points of the well trajectory."""
        return np.vstack(
            [
                self.pipes[0].points,
                *[pipe.points[1:] for pipe in self.pipes[1:]],
            ]
        )

    @property
    def size(self) -> int:
        """Return the number of pipe sections along the well trajectory."""
        return len(self.pipes)
