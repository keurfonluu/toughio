from __future__ import annotations

import copy
import os
import pathlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast, overload

import meshio
import numpy as np
import pvgridder as pvg
import pyvista as pv
from scipy.spatial import KDTree

from .well import WellCasing, WellTrajectory


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Literal, Optional

    from numpy.typing import ArrayLike, NDArray
    from typing_extensions import Self
    
    from toughio.core.output import ElementOutput


class BaseMesh(ABC):
    """Base class for mesh."""

    __name__: str = "BaseMesh"
    __qualname__: str = "toughio.BaseMesh"

    def __init__(
        self,
        *args,
        metadata: Optional[dict] = None,
        **kwargs
    ) -> None:
        """Initialize a mesh."""
        if len(args) == 1:
            (mesh,) = args

            if isinstance(mesh, BaseMesh):
                self._pyvista = mesh.pyvista

            elif isinstance(mesh, (pv.StructuredGrid, pv.UnstructuredGrid)):
                self._pyvista = mesh.copy()

            elif isinstance(mesh, pv.RectilinearGrid):
                self._pyvista = self._cast_to_unstructured_grid(mesh)

            elif isinstance(mesh, pv.ExplicitStructuredGrid):
                self._pyvista = self._cast_to_unstructured_grid(mesh)

            elif isinstance(mesh, meshio.Mesh):
                if mesh.cell_sets:
                    materials = [
                        np.full(len(c.data), -1, dtype=int) for c in mesh.cells
                    ]

                    for i, (k, v) in enumerate(mesh.cell_sets.items()):
                        v = np.asanyarray(v)
                        mesh.field_data[k] = np.array([i + 1, 3])

                        for ii, vv in enumerate(v):
                            if vv is not None and len(vv):
                                materials[ii][vv] = i + 1

                    mesh.cell_data["Material"] = [np.asanyarray(material) for material in materials]

                self._pyvista = pv.from_meshio(mesh)

                if mesh.field_data:
                    self.metadata["Material"] = {
                        k: int(v[0]) for k, v in mesh.field_data.items()
                    }

            elif isinstance(mesh, (str, os.PathLike)):
                if pathlib.Path(mesh).suffix == ".f3grid":
                    self._pyvista = Mesh(meshio.read(mesh)).pyvista

                else:
                    self._pyvista = pv.read(str(mesh))

            else:
                raise ValueError(f"could not initialize mesh from '{type(mesh)}'")

        elif len(args) == 2:
            self._pyvista = pv.from_meshio(meshio.Mesh(*args))

        else:
            raise ValueError()

        if isinstance(self.pyvista, pv.UnstructuredGrid):
            self._pyvista = pvg.extract_cells_by_dimension(
                self.pyvista, keep_empty_cells=True
            )

        # Cache user_dict in metadata for performance
        # Update user_dict with metadata when saving mesh
        self._metadata = (
            copy.deepcopy(metadata) if metadata else dict(self.pyvista.user_dict)
        )

        try:
            material_key = self.material_key

        except KeyError:
            material_key = None

            for k, v in self.data.items():
                if k.lower().startswith("vtk"):
                    continue

                if v.dtype.kind == "i":
                    material_key = k
                    break

        self.material_key = material_key if material_key else "Material"

        if self.label_length is None:
            self.set_label_length()

    @overload
    def __getitem__(self, key: int) -> pv.Cell: ...

    @overload
    def __getitem__(self, key: slice | ArrayLike) -> Self: ...

    def __getitem__(self, key: int | slice | ArrayLike) -> Self | pv.Cell:
        """Slice a mesh."""
        if isinstance(key, int):
            return self.pyvista.get_cell(key)

        else:
            mask = (
                np.arange(self.n_cells)[key]
                if isinstance(key, slice)
                else np.asanyarray(key)
            )
            mesh = self.__class__(
                self._cast_to_unstructured_grid(self.pyvista).extract_cells(mask),
                metadata=self.metadata,
            )
            mesh.labels = self.labels[mask]

            return mesh

    def copy(self, deep: bool = True) -> Self:
        """
        Return a copy of the mesh.

        Parameters
        ----------
        deep : bool, default True
            If True, return a deep copy.

        Returns
        -------
        toughio.Mesh
            Copy of the mesh.

        """
        mesh = self.__class__(self.pyvista.copy(deep=deep))
        mesh.metadata.update(self.metadata)

        return mesh

    def add_data(self, *args) -> None:
        """
        Add a new data array.

        Parameters
        ----------
        name : str
            Name of data array.
        data : ArrayLike
            Data array.

        """
        active = self.active
        n_active = active.sum()
        n_cells = self.n_cells

        def add_active_data(name: str, arr: ArrayLike) -> None:
            """Add active data array."""
            arr = np.asanyarray(arr)

            if len(arr) >= n_cells:
                self.data[name] = arr[:n_cells]

            elif len(arr) == n_active:
                self.data[name] = np.full(
                    (n_cells, arr.shape[1] if arr.ndim > 1 else 1),
                    np.nan,
                    dtype=arr.dtype,
                )
                self.data[name][active] = arr

            else:
                raise ValueError(f"could not add data array '{name}'")

        from .. import ElementOutput

        if len(args) == 1:
            (data,) = args

            if isinstance(data, ElementOutput):
                data = data.data

            if isinstance(data, dict):
                for k, v in data.items():
                    add_active_data(k, v)

            else:
                raise ValueError(f"could not add data from '{type(data)}'")

        elif len(args) == 2:
            name, data = args
            add_active_data(name, data)

        else:
            raise ValueError("invalid input data")

    add_cell_data = add_data

    def add_material(self, material: str, imat: Optional[int] = None) -> None:
        """
        Add a new material.

        Parameters
        ----------
        material : str
            Material name.
        imat : int, optional
            Material ID. Older materials with the same ID will be removed.

        """
        material_key = self.material_key

        if imat is None:
            imat = len(self.metadata[material_key])

        else:
            to_pop = [k for k, v in self.metadata[material_key].items() if v == imat]

            for k in to_pop:
                self.metadata[material_key].pop(k, None)

        self.metadata[material_key][material] = imat

    def extract_cells_by_material(
        self, material: int | str | Sequence[int | str], invert: bool = False
    ) -> Self:
        """
        Extract cells with given material names or IDS.

        Parameters
        ----------
        material : int | str | Sequence[int | str]
            List of material names or IDs to extract.
        invert : bool, default False
            If True, invert selection.

        Returns
        -------
        toughio.Mesh
            Mesh with extracted materials.

        """
        mask = self.find_cells_by_material(material, invert)

        return self[mask]

    def extract_slice(
        self, normal: str | ArrayLike, origin: Optional[ArrayLike] = None
    ) -> Self:
        """
        Extract cells along a plane defined by its origin and normal vector.

        Parameters
        ----------
        normal : {'x', '-x', 'y', '-y', 'z', '-z'} | ArrayLike
            Orientation of normal vector.
        origin : ArrayLike, optional
            Origin of normal vector.

        Returns
        -------
        toughio.Mesh
            Mesh with extracted slice.

        """
        normal = np.asanyarray(normal)
        origin = np.asanyarray(origin) if origin is not None else None
        mesh = self.pyvista.slice(normal, origin=origin).cast_to_unstructured_grid()

        return self.__class__(mesh, metadata=self.metadata)

    def fuse_cells(
        self, ind: Sequence[int] | Sequence[Sequence[int]], inplace: bool = False
    ) -> None | Self:
        """
        Fuse cells.

        Parameters
        ----------
        ind : ArrayLike | Sequence[ArrayLike]
            Indices or sequence of indices of cells to fuse.
        inplace : bool, default False
            If True, modify the current mesh. Otherwise, return a new mesh.

        Returns
        -------
        toughio.Mesh
            Mesh with fused cells. Only provided if *inplace* is False.

        """
        mask = np.ones(self.n_cells, dtype=bool)
        ind_ = [ind] if np.ndim(ind[0]) == 0 else ind

        for ids in ind_:
            ids = np.asanyarray(ids)
            mask[ids[1:]] = False

        pyvista = pvg.fuse_cells(self.pyvista, ind_)
        labels = self.labels[mask]

        if inplace:
            self._pyvista = pyvista
            self.labels = labels

        else:
            mesh = self.__class__(pyvista, metadata=self.metadata, force=True)
            mesh.labels = self.labels[mask]

            return mesh

    def find_cells_by_material(
        self, material: int | str | Sequence[int | str], invert: bool = False
    ) -> NDArray:
        """
        Find cells with given material names or IDS.

        Parameters
        ----------
        material : int | str | Sequence[int | str]
            List of material names or IDs to query.
        invert : bool, default False
            If True, invert selection.

        Returns
        -------
        NDArray
            Indices of cells with given materials.

        """
        material = [material] if isinstance(material, (int, str)) else material

        try:
            material_map = self.metadata[self.material_key]
            material_ = np.unique(
                [mat if isinstance(mat, int) else material_map[mat] for mat in material]
            )

        except KeyError as e:
            raise ValueError(f"invalid material {e}")

        mask = np.isin(self.materials_digitized, material_, invert=invert)

        return np.flatnonzero(mask)

    def find_enclosing_cell(
        self,
        points: ArrayLike,
        material: Optional[int | str | Sequence[int | str]] = None,
    ) -> int | NDArray:
        """
        Find cell(s) that contains query point(s).

        Parameters
        ----------
        points : ArrayLike
            Coordinates of point(s) to query.
        material : int | str | Sequence[int | str], optional
            List of material names or IDs to query.

        Returns
        -------
        int | NDArray
            Indice(s) of cell(s) containing point(s).

        """
        points = np.asanyarray(points)
        mesh = (
            self.extract_cells_by_material(material) if material is not None else self
        )

        ids = mesh.pyvista.find_containing_cell(points)
        ids = (
            np.where(ids >= 0, mesh.data["vtkOriginalCellIds"][ids], -1)
            if material is not None
            else ids
        )

        return int(ids) if np.ndim(ids) == 0 else ids

    def find_nearest_cell(
        self,
        points: ArrayLike,
        material: Optional[int | str | Sequence[int | str]] = None,
    ) -> int | NDArray:
        """
        Find cells(s) nearest to query point(s).

        Parameters
        ----------
        points : ArrayLike
            Coordinates of point(s) to query.
        material : int | str | Sequence[int | str], optional
            List of material names or IDs to query.

        Returns
        -------
        int | NDArray
            Indice(s) of cell(s) nearest to point(s).

        """
        mesh = (
            self.extract_cells_by_material(material) if material is not None else self
        )
        centers = mesh.centers

        mask = ~np.isnan(mesh.centers).any(axis=1)
        ids = KDTree(centers[mask]).query(points)[1]
        ids = np.arange(mesh.n_cells)[mask][ids]
        ids = mesh.data["vtkOriginalCellIds"][ids] if material is not None else ids

        return ids

    near = find_nearest_cell

    def rename_data(self, old: str, new: str) -> None:
        """
        Rename an existing data array.

        Parameters
        ----------
        old : str
            Name of data array to rename.
        new : str
            Name to rename the data array to.

        """
        self.pyvista.rename_array(old, new, preference="cell")

    def set_active(self, active: bool, ind: ArrayLike) -> None:
        """
        Set active state to cells.

        Parameters
        ----------
        active : bool
            Active state to set.
        ind : ArrayLike, optional
            Indices of cells for which active state will be assigned to.

        """
        ind = np.asanyarray(ind)
        
        if "vtkGhostType" not in self.data:
            self.data["vtkGhostType"] = np.zeros(self.n_cells, dtype=np.uint8)

        self.data["vtkGhostType"][ind] = 0 if active else 32

    def set_label_length(self, n: Optional[int] = None) -> None:
        """
        Set label length and regenerate cell label array.

        Parameters
        ----------
        n : int, optional
            Label length.

        """
        from . import Labeler

        if n is None or n == 0:
            bins = 3185000 * 10 ** np.arange(5, dtype=np.int64) + 1
            n = int(np.digitize(self.n_cells, bins)) + 5

        self.labels = Labeler(n)(self.n_cells)
        self.metadata["Label Length"] = n

    def set_label(self, label: str, ind: int) -> None:
        """
        Set label to cell.

        Parameters
        ----------
        Label : str
            Cell label.
        ind : ArrayLike, optional
            Indice of cell for which label will be assigned to.

        """
        if len(label) != self.label_length:
            raise ValueError(
                f"could not set label of length {len(label)} (expected length {self.label_length})"
            )

        self.metadata["Label"][ind] = label

    def set_material(self, material: str, ind: Optional[ArrayLike] = None) -> None:
        """
        Set material to cells.

        Parameters
        ----------
        material : str
            Material name.
        ind : ArrayLike, optional
            Indices of cells for which material will be assigned to.

        """
        ind = np.asanyarray(ind) if ind is not None else np.ones(self.n_cells, dtype=bool)
        material_key = self.material_key

        if material_key not in self.metadata:
            self.metadata[material_key] = {material: 0}

        try:
            imat = self.metadata[material_key][material]

        except KeyError:
            imat = len(self.metadata[material_key])
            self.metadata[material_key][material] = imat

        self.materials_digitized[ind] = imat

    def set_material_by_layer(
        self,
        material: str,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        axis: int = 2,
    ) -> None:
        """
        Set material to cells within defined bounds.

        Parameters
        ----------
        material : str
            Material name.
        vmin : float, optional
            Lower bound value. If None, default to -Infinity.
        vmax : float, optional
            Upper bound value. If None, default to +Infinity.
        axis : int, default 2
            Axis along which filter is applied.

        """
        vmin = vmin if vmin is not None else -np.inf
        vmax = vmax if vmax is not None else np.inf

        v = self.centers[:, axis]
        mask = np.logical_and(v > vmin, v < vmax)
        self.set_material(material, mask)

    def to_meshio(self) -> meshio.Mesh:
        """
        Convert mesh to a meshio mesh.

        Returns
        -------
        meshio.Mesh
            Output mesh.

        """
        return pv.to_meshio(self.pyvista)

    def to_pyvista(self) -> pv.StructuredGrid | pv.UnstructuredGrid:
        """
        Convert mesh to a PyVista mesh.

        Returns
        -------
        pyvista.StructuredGrid | pyvista.UnstructuredGrid
            Output mesh.

        """
        return cast(pv.StructuredGrid | pv.UnstructuredGrid, self.pyvista.copy(deep=True))
    
    @overload
    def to_tough(
        self,
        filename: str | os.PathLike,
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = False,
        incon: bool = False,
        **kwargs,
    ) -> None: ...

    @overload
    def to_tough(
        self,
        filename: None = None,
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = False,
        incon: bool = False,
        **kwargs,
    ) -> dict: ...

    def to_tough(
        self,
        filename: Optional[str | os.PathLike] = None,
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = False,
        incon: bool = False,
        **kwargs,
    ) -> dict | None:
        """
        Convert mesh to TOUGH mesh.

        Parameters
        ----------
        filename : str | os.PathLike, optional
            Output file name.
        material_name : dict, optional
            Map of material names.
        gravity : ArrayLike, optional
            Gravity direction vector.
        assume_orthogonal : bool, default False
            If True, connection properties will be calculated assuming orthogonal
            connection lines.
        incon : bool, default False
            If True, also export initial conditions.
        **kwargs : dict, optional
            Additional keyword arguments. See ``toughio.write_input`` for more details.

        Returns
        -------
        dict
            TOUGH mesh as a dict. Only provided if *filename* is None.

        """

        def dot(A: ArrayLike, B: ArrayLike) -> NDArray:
            """Calculate the dot product when arrays A and B have the same shape."""
            A = np.asanyarray(A)
            B = np.asanyarray(B)

            return (A * B).sum(axis=1)

        def intersection_line_plane(
            centers: ArrayLike, lines: ArrayLike, points: ArrayLike, normals: ArrayLike
        ) -> NDArray:
            """Calculate the intersection point between a line and a plane."""
            centers = np.asanyarray(centers)
            lines = np.asanyarray(lines)
            points = np.asanyarray(points)
            normals = np.asanyarray(normals)
            tmp = dot(points - centers, normals) / dot(lines, normals)

            return centers + lines * tmp[:, None]

        def distance_point_plane(
            centers: ArrayLike, points: ArrayLike, normals: ArrayLike, mask: ArrayLike
        ) -> NDArray:
            """Calculate the orthogonal distance of a point to a plane."""
            centers = np.asanyarray(centers)
            points = np.asanyarray(points)
            normals = np.asanyarray(normals)
            mask = np.asanyarray(mask)

            return np.where(mask, 1.0e-9, np.abs(dot(centers - points, normals)))

        from .. import write_input

        material_name = material_name if material_name else {}
        gravity = gravity if gravity is not None else np.array([0.0, 0.0, -1.0])

        # Shallow copy current mesh
        mesh = self.copy(deep=False)

        labels = mesh.labels
        materials = mesh.materials
        dirichlet = mesh.dirichlet
        volumes = np.where(dirichlet, 1.0e50, mesh.volumes)
        centers = mesh.centers

        # Labels of inactive elements
        inactive = ~mesh.active
        inactive_labels = set(labels[inactive])

        # Connection data
        connections, face_centers, face_normals, face_areas = (
            mesh._compute_connection_properties()
        )
        labels_1 = labels[connections[:, 0]]
        labels_2 = labels[connections[:, 1]]
        centers_1 = centers[connections[:, 0]]
        centers_2 = centers[connections[:, 1]]
        bounds_1 = dirichlet[connections[:, 0]]
        bounds_2 = dirichlet[connections[:, 1]]

        # Direction vectors of connection lines
        lines = centers_2 - centers_1
        lines /= np.linalg.norm(lines, axis=1)[:, None]

        # Nodal distances, permeability directions and gravity angles
        if not assume_orthogonal:
            fp = intersection_line_plane(centers_1, lines, face_centers, face_normals)
            distances_1 = np.where(
                bounds_1, 1.0e-9, np.linalg.norm(centers_1 - fp, axis=1)
            )
            distances_2 = np.where(
                bounds_2, 1.0e-9, np.linalg.norm(centers_2 - fp, axis=1)
            )
            permeability_directions = np.abs(lines).argmax(axis=1) + 1
            angles = lines @ gravity

        else:
            distances_1 = distance_point_plane(
                centers_1, face_centers, face_normals, bounds_1
            )
            distances_2 = distance_point_plane(
                centers_2, face_centers, face_normals, bounds_2
            )
            permeability_directions = np.abs(face_normals).argmax(axis=1) + 1
            angles = np.sign((face_normals * lines).sum(axis=1)) * (
                face_normals @ gravity
            )

        # Write MESH file
        # Elements
        elements = {
            label: {
                "material": (
                    material_name[material] if material in material_name else material
                ),
                "volume": volume,
                "center": center,
            }
            for label, material, volume, center in zip(
                labels, materials, volumes, centers
            )
            if label not in inactive_labels
        }

        # Connections
        connections = {}

        for l1, l2, isot, d1, d2, face_area, angle in zip(
            labels_1,
            labels_2,
            permeability_directions,
            distances_1,
            distances_2,
            face_areas,
            angles,
        ):
            label = f"{l1}{l2}"

            if label in connections:
                connections[label]["nodal_distances"][0] = min(
                    connections[label]["nodal_distances"][0], d1
                )
                connections[label]["nodal_distances"][1] = min(
                    connections[label]["nodal_distances"][1], d2
                )
                connections[label]["interface_area"] += face_area

            else:
                connections[label] = {
                    "permeability_direction": isot,
                    "nodal_distances": [d1, d2],
                    "interface_area": face_area,
                    "gravity_cosine_angle": angle,
                }

        parameters = {"elements": elements, "connections": connections}

        # Initial conditions
        if incon:
            porosities = mesh.porosities
            permeabilities = mesh.permeabilities
            permeabilities = (
                np.expand_dims(permeabilities, axis=1)
                if permeabilities.ndim == 1
                else permeabilities
            )
            phase_compositions = mesh.phase_compositions
            initial_conditions = mesh.initial_conditions
            initial_conditions = (
                np.expand_dims(initial_conditions, axis=1)
                if initial_conditions.ndim == 1
                else initial_conditions
            )
            parameters["initial_conditions"] = {}

            for label, phi, k, index, values in zip(
                labels,
                porosities,
                permeabilities,
                phase_compositions,
                initial_conditions,
            ):
                if label in inactive_labels:
                    continue

                tmp = {}

                if phi != 0.0:
                    tmp["porosity"] = phi

                if (k != 0.0).any():
                    tmp["userx"] = k[:3]

                if index != 0:
                    tmp["phase_composition"] = index

                if (values != 0.0).any():
                    tmp["values"] = values

                if tmp:
                    parameters["initial_conditions"][label] = tmp

        # Add well parameters
        self._add_well_to_tough(parameters, gravity=gravity)

        if filename is not None:
            write_input(filename, parameters, block="mesh", **kwargs)

            if incon:
                write_input(
                    pathlib.Path(filename).parent / "INCON",
                    parameters,
                    block="incon",
                    **kwargs,
                )

        else:
            return parameters

    def to_pvd(
        self,
        filename: str | os.PathLike,
        outputs: Sequence[ElementOutput],
        time_unit: Optional[Literal["second", "hour", "day", "year"]] = None,
    ) -> None:
        """
        Write mesh and outputs to PVD file.

        Parameters
        ----------
        filename : str | PathLike
            Output file name.
        outputs : Sequence[ElementOutput]
            List of element outputs to export.
        time_unit : {'second', 'hour', 'day', 'year'}, optional
            Time steps unit.

        """
        import xml.etree.ElementTree as ET

        filename = pathlib.Path(filename)

        if not filename.name.endswith(".pvd"):
            raise ValueError("could not write PVD file not ending with '.pvd'")

        if filename.parent != pathlib.Path("."):
            filename.parent.mkdir(parents=True, exist_ok=True)

        # Sort outputs by time
        outputs = sorted(outputs, key=lambda x: x.time)

        # Write VTU files for all time steps
        mesh_ = self.copy()
        filenames, time_steps = [], []

        factors = {
            "second": 1.0,
            "hour": 3600.0,
            "day": 86400.0,
            "year": 31557600.0,
        }
        factor = factors[time_unit] if time_unit else 1.0

        for i, output in enumerate(outputs):
            filename_ = filename.name.replace(".pvd", f"_{i}.vtu")
            mesh_.add_data(output)
            mesh_.write(filename.parent / filename_)

            filenames.append(filename_)
            time_steps.append(output.time / factor)

        # Write PVD file
        vtkfile = ET.Element(
            "VTKFile", type="Collection", version="0.1", byte_order="LittleEndian"
        )
        collection = ET.SubElement(vtkfile, "Collection")

        for filename_, time_step in zip(filenames, time_steps):
            ET.SubElement(
                collection,
                "DataSet",
                timestep=str(time_step),
                group="",
                part="0",
                file=filename_,
            )

        tree = ET.ElementTree(vtkfile)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    def to_xdmf(
        self,
        filename: str | os.PathLike,
        other_data: Optional[Sequence[dict]] = None,
        time_steps: Optional[ArrayLike] = None,
    ) -> None:
        """
        Convert mesh to XDMF file.

        Parameters
        ----------
        filename : str | os.PathLike
            Output file name.
        other_data : Sequence[dict], optional
            List of additional data to export.
        time_steps : ArrayLike, optional
            List of time steps.

        """
        import shutil

        filename = pathlib.Path(filename)
        other_data = other_data if other_data else []
        data = [self.data, *other_data]

        nt = len(data)
        time_steps = (
            np.asanyarray(time_steps) if time_steps is not None else np.arange(nt)
        )

        if time_steps is not None and len(time_steps) != nt:
            raise ValueError(
                f"inconsitent number of data ({nt}) and time steps ({len(time_steps)})"
            )

        # Convert to meshio
        mesh = pv.to_meshio(self.pyvista)  # type: ignore
        points = mesh.points
        cells = mesh.cells

        # Split cell data arrays
        sizes = np.cumsum([len(c.data) for c in cells[:-1]])
        data = [{k: np.split(v, sizes) for k, v in cd.items()} for cd in data]

        # Sort data with time steps
        idx = time_steps.argsort()
        data = [data[i] for i in idx]
        time_steps = time_steps[idx]

        # Create parent folder if any
        parent_is_root = str(filename.parent) == "."

        if not parent_is_root:
            filename.parent.mkdir(parents=True, exist_ok=True)

        # Write XDMF
        with meshio.xdmf.TimeSeriesWriter(filename) as writer:
            writer.write_points_cells(points, cells)

            for t, cd in zip(time_steps, data):
                writer.write_data(t, cell_data=cd)

        # Bug in meshio v5: H5 file is written in the current working directory
        if not parent_is_root:
            source = filename.with_suffix(".h5")

            if source.is_file():
                os.remove(source)

            shutil.move(source.name, filename.parent)

    def write_tough(
        self,
        filename: str | os.PathLike = "MESH",
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = False,
        incon: bool = False,
        **kwargs,
    ) -> None:
        """
        Write mesh to TOUGH MESH file.

        Parameters
        ----------
        filename : str | os.PathLike, default 'MESH'
            Output file name.
        material_name : dict, optional
            Map of material names.
        gravity : ArrayLike, optional
            Gravity direction vector.
        assume_orthogonal : bool, default False
            If True, connection properties will be calculated assuming orthogonal
            connection lines.
        incon : bool, default False
            If True, also export initial conditions to INCON file.
        **kwargs : dict, optional
            Additional keyword arguments. See ``toughio.write_input`` for more details.

        """
        self.to_tough(
            filename,
            material_name,
            gravity,
            assume_orthogonal,
            incon,
        )

    def write(
        self, filename: str | os.PathLike, file_format: Optional[str] = None
    ) -> None:
        """
        Write mesh to file.

        Parameters
        ----------
        filename : str | os.PathLike
            Output file name.
        file_format : str, optional
            Output file format.

        """
        if file_format:
            self.to_meshio().write(filename, file_format=file_format)

        else:
            self.pyvista.user_dict.update(self.metadata)
            self.pyvista.save(str(filename))

    save = write  # alias

    def plot(
        self,
        plotter: Optional[pv.Plotter] = None,
        *,
        xscale: Optional[float] = None,
        yscale: Optional[float] = None,
        zscale: Optional[float] = None,
        parallel_projection: bool = False,
        enable_picking: bool = False,
        tolerance: float = 0.0,
        **kwargs,
    ) -> None:
        """
        Plot a mesh.

        Parameters
        ----------
        plotter : pyvista.Plotter, optional
            Active plotter.
        xscale : float, optional
            Scaling in the X direction.
        yscale : float, optional
            Scaling in the Y direction.
        zscale : float, optional
            Scaling in the Z direction.
        parallel_projection : bool, default False
            If True, enable parallel projection.
        enable_picking : bool, default False
            If True, enable cell picking with right-click.
        tolerance : float, default 0.0
            Specify tolerance for performing pick operation.
        **kwargs : dict, optional
            Additional keyword arguments. See ``pyvista.Plotter`` and
            ``pyvista.Plotter.add_mesh`` for more details.

        """
        default_kwargs = {
            "scalars": self.materials,
            "show_edges": True,
            "scalar_bar_args": {
                "vertical": True,
                "position_y": 0.1,
                "height": 0.8,
            },
        }
        default_kwargs.update(kwargs)

        # Ghost cells are not hidden for 2D structured grids
        # See <https://github.com/pyvista/pyvista/issues/7112>
        mesh = self._cast_to_unstructured_grid(self.pyvista)

        # Plot
        if plotter is None:
            plotter_kwargs = {}

            for keyword in {"notebook", "title"}:
                if keyword in default_kwargs:
                    plotter_kwargs[keyword] = default_kwargs.pop(keyword)

            p = pv.Plotter(**plotter_kwargs)

        else:
            p = plotter

        if xscale or yscale or zscale:
            p.set_scale(xscale, yscale, zscale)  # type: ignore

        p.add_mesh(mesh, **default_kwargs)

        if enable_picking:
            infos = p.add_text(
                "",
                position="upper_left",
                font_size=12,
                shadow=False,
            )
            labels = self.labels
            materials = self.materials
            values = (
                mesh.cell_data[default_kwargs["scalars"]]
                if isinstance(default_kwargs["scalars"], str)
                else default_kwargs["scalars"]
            )

            def callback(mesh: pv.DataSet) -> None:
                i = mesh.cell_data["vtkOriginalCellIds"][0]
                label = labels[i]
                coords = np.round(mesh.get_cell(0).center, 3)
                material = materials[i]
                value = values[i]
                out = f"{label}\nCoords: ({', '.join(map(str, coords))})\nMaterial: {material}\nValue: {value}"

                infos.SetText(2, out)
                p.update()

            p.enable_element_picking(
                mode="cell",
                callback=callback,
                show_message=False,
                tolerance=tolerance,
                picker="cell",  # type: ignore
            )

        p.add_axes()  # type: ignore

        if parallel_projection:
            p.enable_parallel_projection()  # type: ignore

        if plotter is None:
            p.show()

    @abstractmethod
    def _add_well_to_tough(self, parameters: dict, **kwargs) -> None:
        """
        Add well to TOUGH mesh parameters.

        Parameters
        ----------
        parameters : dict
            TOUGH mesh parameters.

        """
        pass

    @staticmethod
    def _cast_to_unstructured_grid(mesh: pv.DataSet) -> pv.UnstructuredGrid:
        """
        Properly cast mesh to unstructured grid.

        Note
        ----
        This method prevents the conversion of ghost cells to empty cells.

        """
        mesh = mesh.copy(deep=False)

        if "vtkGhostType" in mesh.cell_data:
            tmp = mesh.cell_data.pop("vtkGhostType")

        else:
            tmp = None

        out = mesh.cast_to_unstructured_grid()

        if tmp is not None:
            out.cell_data["vtkGhostType"] = tmp

        return out

    def _compute_connection_properties(
        self,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """Compute connection properties."""
        poly = pvg.extract_cell_geometry(
            self.pyvista, remove_ghost_cells=True
        ).compute_cell_sizes(length=True, area=True, volume=False)
        mask = (poly.cell_data["vtkOriginalCellIds"] >= 0).all(axis=1)
        connections = poly.cell_data["vtkOriginalCellIds"][mask]
        centers = poly.cell_centers(vertex=False).points[mask]

        if self.ndim == 3:
            normals = poly.compute_normals(point_normals=False)["Normals"][mask]
            lengths_or_areas = poly.cell_data["Area"][mask]

        else:
            normals = np.diff(
                poly.points[
                    np.delete(poly.lines.reshape((poly.n_lines, 3)), 0, axis=1)
                ],
                axis=1,
            ).squeeze()
            normals = np.column_stack(
                (normals[:, 2], np.zeros(poly.n_lines), -normals[:, 0])
            )
            normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
            normals = normals[mask]
            lengths_or_areas = poly.cell_data["Length"][mask]

        return connections, centers, normals, lengths_or_areas

    def _get_property(
        self, name: str, default: Optional[ArrayLike] = None
    ) -> NDArray:
        """Get property data."""
        if name not in self.data:
            data = np.zeros(self.n_cells, dtype=float) if default is None else np.asanyarray(default)
            self.data[name] = data

        return self.data[name]

    @property
    def active(self) -> NDArray:
        """Return active cell array."""
        return (
            self._get_property("vtkGhostType", np.zeros(self.n_cells, dtype=np.uint8))
            == 0
        )

    @property
    def centers(self) -> NDArray:
        """Return cell center array."""
        return pvg.get_cell_centers(self.pyvista)  # type: ignore

    @property
    def data(self) -> pv.DataSetAttributes:
        """Return mesh data."""
        return self.pyvista.cell_data

    cell_data = data

    @property
    def dirichlet(self) -> NDArray:
        """Return Dirichlet cell array."""
        return self._get_property("Dirichlet", np.zeros(self.n_cells, dtype=bool))

    @dirichlet.setter
    def dirichlet(self, value: ArrayLike) -> None:
        """Set Dirichlet cell array."""
        self.add_data("Dirichlet", np.asanyarray(value).astype(bool))

    @property
    def initial_conditions(self) -> NDArray:
        """Return initial conditions array."""
        return self._get_property("Initial Conditions")

    @initial_conditions.setter
    def initial_conditions(self, value: ArrayLike) -> None:
        """Set initial conditions array."""
        self.add_data("Initial Conditions", np.asanyarray(value).astype(float))

    @property
    def labels(self) -> NDArray:
        """Return cell labels."""
        return np.asanyarray(self.metadata["Label"])

    @labels.setter
    def labels(self, value: ArrayLike) -> None:
        """Set cell labels."""
        value = np.asanyarray(value)
        self.metadata["Label"] = list(map(str, value))
        self.metadata["Label Length"] = len(max(value, key=len))

    @property
    def label_length(self) -> int | None:
        """Return label length."""
        try:
            return self.metadata["Label Length"]

        except KeyError:
            return None

    @label_length.setter
    def label_length(self, value: int | None) -> None:
        """Set label length."""
        self.set_label_length(value)

    @property
    def material_key(self) -> str:
        """Return data key used for materials."""
        return self.metadata["Material Key"]

    @material_key.setter
    def material_key(self, value: str) -> None:
        """Set data key used for materials."""
        try:
            if self.data[value].dtype.kind != "i":
                raise ValueError("could not set material to non-integer data")

        except KeyError:
            pass

        self.metadata["Material Key"] = value

    @property
    def materials(self) -> NDArray:
        """Return cell materials. Always return a copy."""
        metadata = self.metadata

        try:
            material_map = {v: k for k, v in metadata[self.material_key].items()}

            return np.array(
                [
                    material_map[material] if material in material_map else material
                    for material in self.materials_digitized
                ]
            )

        except KeyError:
            return self.materials_digitized.copy()

    @property
    def materials_digitized(self) -> NDArray:
        """Return cell material IDs."""
        return self._get_property(self.material_key, -np.ones(self.n_cells, dtype=int))

    @materials_digitized.setter
    def materials_digitized(self, value: ArrayLike) -> None:
        """Set cell material IDs."""
        self.add_data(self.material_key, np.asanyarray(value).astype(int))

    @property
    def metadata(self) -> dict:
        """Return mesh metadata."""
        return self._metadata

    @property
    def ndim(self) -> int:
        """Return mesh dimension."""
        return pvg.get_dimension(self.pyvista)

    @property
    def n_cells(self) -> int:
        """Return number of cells."""
        return self.pyvista.n_cells

    @property
    def n_points(self) -> int:
        """Return number of points."""
        return self.pyvista.n_points

    @property
    def permeabilities(self) -> NDArray:
        """Return cell permeability array."""
        return self._get_property("Permeability")

    @permeabilities.setter
    def permeabilities(self, value: ArrayLike) -> None:
        """Set cell permeability array."""
        self.add_data("Permeability", np.asanyarray(value).astype(float))

    @property
    def phase_compositions(self) -> NDArray:
        """Return phase composition array."""
        return self._get_property(
            "Phase Composition", np.zeros(self.n_cells, dtype=int)
        )

    @phase_compositions.setter
    def phase_compositions(self, value: ArrayLike) -> None:
        """Set phase composition array."""
        self.add_data("Phase Composition", np.asanyarray(value).astype(int))

    @property
    def points(self) -> NDArray:
        """Return points array."""
        return self.pyvista.points

    @property
    def porosities(self) -> NDArray:
        """Return cell porosity array."""
        return self._get_property("Porosity")

    @porosities.setter
    def porosities(self, value: ArrayLike) -> None:
        """Set cell porosity array."""
        self.add_data("Porosity", np.asanyarray(value).astype(float))

    @property
    def pyvista(self) -> pv.StructuredGrid | pv.UnstructuredGrid:
        """Return underlying PyVista mesh."""
        return cast(pv.StructuredGrid | pv.UnstructuredGrid, self._pyvista)

    @property
    def volumes(self) -> NDArray:
        """Return cell volume array."""
        is3d = self.ndim == 3
        key = "Volume" if is3d else "Area"

        return np.abs(
            self.pyvista
            .compute_cell_sizes(length=False, area=not is3d, volume=is3d)
            .cell_data[key]
        )


class Mesh(BaseMesh):
    """
    Mesh class.

    Parameters
    ----------
    args : str | PathLike | pyvista.DataSet | meshio.Mesh | toughio.Mesh | ArrayLike
        Initialize a new mesh instance:

         - From a file
         - From a toughio, meshio or PyVista mesh
         - From two points and cells arrays

    material : str, optional
        Cell data key to use to initialize material data.
    metadata : dict, optional
        Mesh metadata.

    """

    __name__: str = "Mesh"
    __qualname__: str = "toughio.Mesh"

    def __init__(
        self,
        *args,
        metadata: Optional[dict] = None,
    ) -> None:
        """Initialize a mesh."""
        super().__init__(*args, metadata=metadata)
        self._wells = []

    def add_well(
        self,
        well: WellTrajectory,
        min_length: float = 1.0e-4,
        tolerance: float = 1.0e-8,
    ) -> WellTrajectory:
        """
        Add a well trajectory.

        Parameters
        ----------
        well : toughio.WellTrajectory
            Well trajectory to add.
        min_length : float, default 1.0e-4
            The minimum length of an intersection. Only used if the well trajectory has
            not been intersected yet.
        tolerance : float, default 1.0e-8
            The absolute tolerance to use to find cells along the trajectory. Only used
            if the well trajectory has not been intersected yet.

        Returns
        -------
        toughio.WellTrajectory
            The intersected well trajectory.

        """
        if not isinstance(well, WellTrajectory):
            raise TypeError("could not add well: expected a WellTrajectory instance")

        if "IntersectedCellIds" not in well.to_pyvista().cell_data:
            well = well.intersect(self, min_length, tolerance)

        self.wells.append(well)

        return well

    def extrude_to_3d(self, height: ArrayLike = 1.0, axis: int = 2) -> Self:
        """
        Convert a 2D mesh to 3D by extruding cells along given axis.

        Parameters
        ----------
        height : ArrayLike, default 1.0
            Height of extrusion.
        axis : int, default 2
            Axis along which extrusion is performed.

        Returns
        -------
        toughio.Mesh
            Extruded mesh. Only provided if *inplace* is False.

        """
        from ..legacy import extrude_to_3d

        return self.__class__(extrude_to_3d(self.pyvista, height, axis))

    def prune_duplicates(self) -> Mesh:
        """
        Delete duplicate points.

        Returns
        -------
        toughio.Mesh
            Mesh with duplicate points removed.

        """
        return Mesh(self.pyvista.clean(produce_merge_map=False))

    def _add_well_to_tough(self, parameters: dict, gravity: ArrayLike) -> None:
        """
        Add well to TOUGH mesh parameters.

        Parameters
        ----------
        parameters : dict
            TOUGH mesh parameters.

        """
        from scipy.spatial.transform import Rotation

        from . import Labeler

        offset = self.n_cells
        labels = self.labels
        incon = "initial_conditions" in parameters

        for i, well in enumerate(self.wells):
            well = well.to_pyvista().compute_cell_sizes(
                length=True, area=False, volume=False
            )
            well = cast(pv.PolyData, well)

            # Define well labels
            well_labels = Labeler(self.label_length)(well.n_cells, offset)
            well_labels[0] = f"#WH{i + 1:02d}"

            # Define well elements and well to rock connections
            # Define initial conditions if any
            well_elements = {}
            well_rock_connections = {}
            well_initial_conditions = {}
            well_sizes = {}

            for label, line in zip(well_labels, pvg.split_lines(well, as_lines=True)):
                radius = line.cell_data["Radius"][0]
                length = line.cell_data["Length"][0]
                material = line.cell_data["Material"][0]
                intersected_cell_id = line.cell_data["IntersectedCellIds"][0]
                area = np.pi * radius**2
                interface_area = length * 2.0 * np.pi * radius

                # Define well element
                well_elements[label] = {
                    "material": material,
                    "volume": length * area,
                    "center": np.array(line.center),
                }
                well_sizes[label] = {"length": length, "area": area}

                # Well trajectory does not intersect the mesh
                if intersected_cell_id == -1:
                    well_elements[label]["heat_exchange_area"] = interface_area

                # Well trajectory intersects the mesh
                else:
                    l2 = labels[intersected_cell_id]

                    # Check volume
                    vol1 = well_elements[label]["volume"]
                    vol2 = parameters["elements"][l2]["volume"]

                    if vol1 >= vol2:
                        raise ValueError(
                            "could not embed a well element in a rock element with smaller volume"
                        )

                    # Calculate gravity cosine angle rotating direction vector by 90 degrees
                    v1 = line.points[1] - line.points[0]
                    v2 = line.points[0] + gravity
                    v1 /= np.linalg.norm(v1)
                    v2 /= np.linalg.norm(v2)

                    if abs(v1 @ v2) == 1.0:
                        gravity_cosine_angle = 0.0

                    else:
                        rotvec = np.cross(v1, v2)
                        rotvec /= np.linalg.norm(rotvec)
                        dvec = Rotation.from_rotvec(0.5 * np.pi * rotvec).apply(v1)
                        gravity_cosine_angle = (dvec / np.linalg.norm(dvec)) @ gravity

                    # Calculate nodal distance using equivalent mass approach
                    r2 = ((vol2 - vol1) / (np.pi * length) + radius**2) ** 0.5
                    d2 = 0.5 * (r2 - radius)

                    well_rock_connections[f"{label}{l2}"] = {
                        "permeability_direction": 1,
                        "nodal_distances": [0.01, d2],
                        "interface_area": interface_area,
                        "gravity_cosine_angle": gravity_cosine_angle,
                    }

                    # Remove embedded well volume from rock element
                    parameters["elements"][l2]["volume"] -= vol1

                # Initial conditions
                if incon:
                    well_initial_conditions[label] = {
                        "values": list(
                            map(
                                lambda x: None if np.isnan(x) else x,
                                line.cell_data["Initial Conditions"][0],
                            ),
                        ),
                    }

            # Define well to well connections
            well_well_connections = {}

            for l1, l2 in zip(well_labels[:-1], well_labels[1:]):
                area1, area2 = well_sizes[l1]["area"], well_sizes[l2]["area"]
                length1, length2 = well_sizes[l1]["length"], well_sizes[l2]["length"]
                center1, center2 = (
                    well_elements[l1]["center"],
                    well_elements[l2]["center"],
                )

                dvec = center2 - center1
                well_well_connections[f"{l1}{l2}"] = {
                    "permeability_direction": 3,
                    "nodal_distances": [0.5 * length1, 0.5 * length2],
                    "interface_area": min(area1, area2),
                    "gravity_cosine_angle": (dvec / np.linalg.norm(dvec)) @ gravity,
                }

            # Update parameters
            parameters["elements"].update(well_elements)
            parameters["connections"].update(well_well_connections)
            parameters["connections"].update(well_rock_connections)

            if incon:
                parameters["initial_conditions"].update(well_initial_conditions)

            # Increment offset
            offset += well.n_cells

    @property
    def wells(self) -> list[WellTrajectory]:
        """
        Return well trajectories.

        Returns
        -------
        list[toughio.WellTrajectory]
            List of well trajectories.

        """
        return self._wells


class CylindricMesh(BaseMesh):
    __name__: str = "CylindricMesh"
    __qualname__: str = "toughio.CylindricMesh"

    def __init__(
        self,
        *args,
        metadata: Optional[dict] = None,
        force: bool = False,
    ) -> None:
        """
        Cylindric mesh class.

        Parameters
        ----------
        args : str | os.PathLike | pyvista.DataSet | toughio.Mesh
            Initialize a new mesh instance:

             - From a file
             - From a toughio or PyVista mesh

            Mesh should represent a 2D vertical rectilinear grid.

        material : str, optional
            Cell data key to use to initialize material data.
        metadata : dict, optional
            Mesh metadata.
        force : bool, default False
            If True, do not check if mesh is a 2D vertical rectilinear grid (may yield
            unexpected results).

        """
        super().__init__(*args, metadata=metadata)

        if self.ndim != 2:
            raise ValueError("could not initialize a cylindric mesh from a 3D mesh")

        x = np.unique(self.points[:, 0])
        z = np.unique(self.points[:, 2])

        if not force:
            if not isinstance(self.pyvista, pv.StructuredGrid):
                raise ValueError(
                    "could not initialize a cylindric mesh from an unstructured mesh"
                )

            if self.pyvista.dimensions[1] != 1:
                raise ValueError(
                    "could not initialize a cylindric mesh from a non vertical mesh"
                )

            if x.size * z.size != np.prod(self.pyvista.dimensions):
                raise ValueError(
                    "could not initialize a cylindric mesh from a non rectilinear mesh"
                )

        self.points[:, 0] -= x[0]
        self.points[:, 1] = 0.0

    @overload
    def __getitem__(self, key: int) -> pv.Cell: ...

    @overload
    def __getitem__(self, key: slice | ArrayLike) -> Self: ...

    def __getitem__(self, key: int | slice | ArrayLike) -> Self | pv.Cell:
        """Slice a mesh."""
        if isinstance(key, int):
            return self.pyvista.get_cell(key)

        else:
            mask = (
                np.arange(self.n_cells)[key]
                if isinstance(key, slice)
                else np.asanyarray(key)
            )
            mesh = self.__class__(
                self._cast_to_unstructured_grid(self.pyvista).extract_cells(mask),
                metadata=self.metadata,
                force=True,
            )
            mesh.labels = self.labels[mask]

            return mesh

    def _compute_connection_properties(
        self,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        """Compute connection properties."""
        connections, centers, normals, lengths = (
            super()._compute_connection_properties()
        )

        # This is counterintuitive but the areas can be calculated with the same
        # instruction given the definitions of x (center) and L (length) for horizontal
        # and vertical connections:
        #  - horizontal: x is the coordinate of the vertical interface (i.e., radius)
        #    and L its "height"
        #       A = (2 * pi * x) * L
        #  - vertical: x is the center of the horizontal interface and L its "width"
        #       A = pi * (rout ** 2 - rin ** 2)
        #         = pi * ((x + L / 2) ** 2 - (x - L / 2) ** 2)
        #         = pi * (2 * x * L)
        areas = 2.0 * np.pi * centers[:, 0] * lengths

        return connections, centers, normals, areas

    def add_well(self, well: WellCasing) -> None:
        """
        Apply a wellbore design to a mesh.

        Parameters
        ----------
        well : toughio.WellCasing
            Wellbore design to apply.

        """
        centers = self.centers
        x = np.unique(self.points[:, 0])

        if not np.isin(well.radii, x).all():
            raise ValueError(
                "could not generate wellbore with radius not matching radial discretization of porous medium"
            )

        well_domain = np.full(self.n_cells, -1)
        cells_to_fuse = []

        for id_, pipe in reversed(list(enumerate(well.pipes))):
            mask = (
                (centers[:, 0] < pipe.inner_radius + pipe.thickness)
                & (centers[:, 2] > pipe.zmin)
                & (centers[:, 2] < pipe.zmax)
            )
            self.set_material(pipe.material, mask)
            self.set_active(True, mask)
            well_domain[mask] = -id_ if pipe.is_porous else id_

            # Find horizontally connected cells to be fused to ensure 1D vertical flow in wellbore
            pipe_centers = centers[mask]

            if not pipe.is_porous and np.ptp(pipe_centers[:, 0]) > 0.0:
                for z in np.unique(pipe_centers[:, 2]):
                    cells_to_fuse.append(
                        np.flatnonzero(np.logical_and(mask, centers[:, 2] == z))
                    )

        self.data["WellDomain"] = well_domain

        # Fuse cells (this will change the mesh to an unstructured grid)
        # Only fuse cells with the same material ID
        cells_to_fuse = [
            ids for ids in cells_to_fuse if np.ptp(self.materials_digitized[ids]) == 0
        ]

        if cells_to_fuse:
            self.fuse_cells(cells_to_fuse, inplace=True)

        # Connections
        connections = {}

        for connection in well.connections:
            pipe1, pipe2 = connection["pipe1"], connection["pipe2"]

            # Well-well connection
            id1 = well.pipes.index(pipe1)

            if pipe2 is not None:
                id2 = well.pipes.index(pipe2)
                key = f"{min(id1, id2)}-{max(id1, id2)}"

            # Well-formation connection
            else:
                key = str(id1)

            connections.setdefault(key, []).append(
                {
                    "type": str(connection["type"]),
                    "zmin": float(connection["zmin"]),
                    "zmax": float(connection["zmax"]),
                }
            )

        if connections:
            self.metadata["WellConnection"] = connections

        # Wellheads
        for i, wellhead in enumerate(well.wellheads):
            whid = self.find_nearest_cell(
                (wellhead.inner_radius, 0.0, wellhead.zmax), material=wellhead.material
            )
            self.set_label(f"#WH{i + 1:02d}", int(whid))

    def copy(self, deep: bool = True) -> Self:
        """
        Return a copy of the mesh.

        Parameters
        ----------
        deep : bool, default True
            If True, return a deep copy.

        Returns
        -------
        toughio.Mesh
            Copy of the mesh.

        """
        mesh = self.__class__(self.pyvista.copy(deep=deep), force=True)
        mesh.metadata.update(self.metadata)

        return mesh
    
    @overload
    def to_tough(
        self,
        filename: str | os.PathLike,
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = True,
        incon: bool = False,
        **kwargs,
    ) -> None: ...

    @overload
    def to_tough(
        self,
        filename: None = None,
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = True,
        incon: bool = False,
        **kwargs,
    ) -> dict: ...

    def to_tough(
        self,
        filename: Optional[str | os.PathLike] = None,
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        assume_orthogonal: bool = True,
        incon: bool = False,
        **kwargs,
    ) -> dict | None:
        """
        Convert mesh to TOUGH mesh.

        Parameters
        ----------
        filename : str | os.PathLike, optional
            Output file name.
        material_name : dict, optional
            Map of material names.
        gravity : ArrayLike, optional
            Gravity direction vector.
        assume_orthogonal : bool, default True
            If True, connection properties will be calculated assuming orthogonal
            connection lines.
        incon : bool, default False
            If True, also export initial conditions.
        **kwargs : dict, optional
            Additional keyword arguments. See ``toughio.write_input`` for more details.

        Returns
        -------
        dict
            TOUGH mesh as a dict. Only provided if *filename* is None.

        """
        return super().to_tough(
            filename=filename,
            material_name=material_name,
            gravity=gravity,
            assume_orthogonal=assume_orthogonal,
            incon=incon,
            **kwargs,
        )

    def _add_well_to_tough(self, parameters: dict, **kwargs) -> None:
        """
        Add well to TOUGH mesh parameters.

        Parameters
        ----------
        parameters : dict
            TOUGH mesh parameters.

        """
        well_domain = self.data.get("WellDomain", np.full(self.n_cells, -1))

        if well_domain is not None and (well_domain >= 0).any():
            label_length = self.label_length
            label_map = {label: i for i, label in enumerate(self.labels)}
            well_connections = self.metadata.get("WellConnection", {})
            well_isots = {
                "well": {"branch": 3, "heat": -1, "forward": 4, "backward": 5},
                "formation": {
                    "heat": -1,
                    "perforation": 1,
                    "gas": 4,
                    "liquid": 5,
                    "backward": 6,
                },
            }

            # Update connections
            connections = {}

            for k, v in parameters["connections"].items():
                l1, l2 = k[:label_length], k[label_length:]
                i1, i2 = label_map[l1], label_map[l2]
                wid1, wid2 = int(well_domain[i1]), int(well_domain[i2])

                # Well connections
                if wid1 >= 0 or wid2 >= 0:
                    # Well-well connection
                    if f"{min(wid1, wid2)}-{max(wid1, wid2)}" in well_connections:
                        key = "well"
                        connection_key = f"{min(wid1, wid2)}-{max(wid1, wid2)}"

                    # Vertical well-formation connection
                    elif (
                        f"{min(abs(wid1), abs(wid2))}-{max(abs(wid1), abs(wid2))}"
                        in well_connections
                    ):
                        key = "formation"
                        connection_key = (
                            f"{min(abs(wid1), abs(wid2))}-{max(abs(wid1), abs(wid2))}"
                        )

                    # Well-formation connection
                    elif str(wid1) in well_connections or str(wid2) in well_connections:
                        key = "formation"

                        if str(wid1) in well_connections:
                            connection_key = str(wid1)

                        else:
                            connection_key = str(wid2)

                    else:
                        connection_key = None

                    # Horizontal connections
                    if v["gravity_cosine_angle"] == 0.0:
                        # Update ISOT
                        isot = -1

                        if connection_key is not None:
                            matched_connection = None

                            for connection in well_connections[connection_key]:
                                zmin, zmax = connection["zmin"], connection["zmax"]
                                z1 = parameters["elements"][l1]["center"][2]
                                z2 = parameters["elements"][l2]["center"][2]

                                if zmin <= z1 <= zmax and zmin <= z2 <= zmax:
                                    matched_connection = connection
                                    break

                            if matched_connection is not None:
                                type_ = matched_connection["type"]

                                if type_ == "none":
                                    continue

                                else:
                                    isot = well_isots[key][type_]

                            # Remove well-well connection
                            elif key == "well":
                                continue

                        v["permeability_direction"] = isot

                        # Set nodal distance to zero for well elements
                        if wid1 >= 0:
                            v["nodal_distances"][0] = 1.0e-9

                        if wid2 >= 0:
                            v["nodal_distances"][1] = 1.0e-9

                    # Vertical connections
                    else:
                        if connection_key is not None:
                            none_connection = False

                            for connection in well_connections[connection_key]:
                                if connection["type"] == "none":
                                    none_connection = True
                                    continue

                            if none_connection:
                                continue

                connections[k] = v

            parameters["connections"] = connections

    @property
    def volumes(self) -> NDArray:
        """Return cell volume array."""
        get_min_max = lambda arr: (arr.min(), arr.max())
        cells = pvg.get_cell_connectivity(self._cast_to_unstructured_grid(self.pyvista))
        xmin, xmax = np.transpose(
            [get_min_max(self.points[:, 0][cell]) for cell in cells]
        )
        zmin, zmax = np.transpose(
            [get_min_max(self.points[:, 2][cell]) for cell in cells]
        )

        return np.pi * (xmax**2 - xmin**2) * (zmax - zmin)
