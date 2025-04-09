from __future__ import annotations

import copy
import os
import pathlib
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Literal, Optional

import meshio
import numpy as np
import pvgridder as pvg
import pyvista as pv
from numpy.typing import ArrayLike
from scipy.spatial import KDTree
from typing_extensions import Self

from ._typing import GridLike
from .well import WellCasing


class BaseMesh(ABC):
    """Base class for mesh."""

    __name__: str = "BaseMesh"
    __qualname__: str = "toughio.BaseMesh"

    def __init__(
        self,
        *args,
        metadata: Optional[dict] = None,
    ) -> None:
        """Initialize a mesh."""
        if len(args) == 1:
            mesh, = args

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
                    mesh.cell_data["Material"] = [np.full(len(c.data), -1, dtype=int) for c in mesh.cells]

                    for i, (k, v) in enumerate(mesh.cell_sets.items()):
                        mesh.field_data[k] = np.array([i + 1, 3])

                        for ii, vv in enumerate(v):
                            if vv is not None and len(vv):
                                mesh.cell_data["Material"][ii][vv] = i + 1
                
                self._pyvista = pv.from_meshio(mesh)

                if mesh.field_data:
                    self.metadata["Material"] = {k: int(v[0]) for k, v in mesh.field_data.items()}

            elif isinstance(mesh, (str, os.PathLike)):
                if pathlib.Path(mesh).suffix == ".f3grid":
                    self._pyvista = Mesh(meshio.read(mesh)).pyvista

                else:
                    self._pyvista = pv.read(mesh)

            else:
                raise ValueError(f"could not initialize mesh from '{type(mesh)}'")

        elif len(args) == 2:
            self._pyvista = pv.from_meshio(meshio.Mesh(*args))

        else:
            raise ValueError()

        if isinstance(self.pyvista, pv.UnstructuredGrid):
            self._pyvista = pvg.extract_cells_by_dimension(self.pyvista, keep_empty_cells=True)

        # Cache user_dict in metadata for performance
        # Update user_dict with metadata when saving mesh
        self._metadata = copy.deepcopy(metadata) if metadata else dict(self.pyvista.user_dict)

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

    def __getitem__(self, key: tuple[int | slice | ArrayLike]) -> Self:
        """Slice a mesh."""
        if isinstance(key, int):
            return self.pyvista.get_cell(key)

        else:
            mesh = self.__class__(self._cast_to_unstructured_grid(self.pyvista).extract_cells(key), metadata=self.metadata)
            mesh.labels = self.labels[key]

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
        from .. import ElementOutput

        if len(args) == 1:
            data, = args

            if isinstance(data, ElementOutput):
                data = data.data

            if isinstance(data, dict):
                for k, v in data.items():
                    self.data[k] = v[:self.n_cells]

            else:
                raise ValueError(f"could not add data from '{type(data)}'")

        elif len(args) == 2:
            name, data = args
            self.data[name] = data[:self.n_cells]

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

    def extract_cells_by_material(self, material: int | str | Sequence[int | str], invert: bool = False) -> Mesh:
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

    def extract_slice(self, normal: str | ArrayLike, origin: Optional[ArrayLike] = None) -> toughio.Mesh:
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
        mesh = self.pyvista.slice(normal, origin=origin).cast_to_unstructured_grid()

        return Mesh(mesh, metadata=self.metadata)

    def fuse_cells(self, ind: ArrayLike | Sequence[ArrayLike], inplace: bool = False) -> None | Self:
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
            
        for ids in ind:
            mask[ids[1:]] = False

        pyvista = pvg.fuse_cells(self.pyvista, ind)
        labels = self.labels[mask]

        if inplace:
            self._pyvista = pyvista
            self.labels = labels

        else:
            mesh = self.__class__(pyvista, metadata=self.metadata, force=True)
            mesh.labels = self.labels[mask]

            return mesh

    def find_cells_by_material(self, material: int | str | Sequence[int | str], invert: bool = False) -> ArrayLike:
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
        ArrayLike
            Indices of cells with given materials.

        """
        material = [material] if isinstance(material, (int, str)) else material

        try:
            material_map = self.metadata[self.material_key]
            material = np.unique([mat if isinstance(mat, int) else material_map[mat] for mat in material])

        except KeyError as e:
            raise ValueError(f"invalid material {e}")

        mask = np.zeros(self.n_cells, dtype=bool)

        for mat in material:
            mask[self.materials_digitized == mat] = True

        mask = ~mask if invert else mask

        return np.flatnonzero(mask)

    def find_enclosing_cell(
        self,
        points: ArrayLike,
        material: Optional[int | str | Sequence[int | str]] = None,
    ) -> ArrayLike:
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
        ArrayLike
            Indice(s) of cell(s) containing point(s).

        """
        mesh = (
            self.extract_cells_by_material(material)
            if material is not None
            else self
        )

        ids = mesh.pyvista.find_containing_cell(points)
        ids = (
            np.where(ids >= 0, mesh.data["vtkOriginalCellIds"][ids], -1)
            if material is not None
            else ids
        )
            
        return np.int64(ids) if np.ndim(ids) == 0 else ids

    def find_nearest_cell(
        self,
        points: ArrayLike,
        material: Optional[int | str | Sequence[int | str]] = None,
    ) -> ArrayLike:
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
        ArrayLike
            Indice(s) of cell(s) nearest to point(s).

        """
        mesh = (
            self.extract_cells_by_material(material)
            if material is not None
            else self
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

        if not n:
            bins = 3185000 * 10 ** np.arange(5, dtype=np.int64) + 1
            n = np.digitize(self.n_cells, bins) + 5

        self.labels = Labeler(n)(self.n_cells)
        self.metadata["Label Length"] = int(n)

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
            raise ValueError(f"could not set label of length {len(label)} (expected length {self.label_length})")

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
        ind = ind if ind is not None else np.ones(self.n_cells, dtype=bool)
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
        return self.pyvista.copy(deep=True)

    def to_tough(
        self,
        filename: Optional[str | os.PathLike] = None,
        nodal_distance: Literal["line", "orthogonal"] = "line",
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        incon: bool = False,
        **kwargs
    ) -> dict | None:
        """
        Convert mesh to TOUGH mesh.

        Parameters
        ----------
        filename : str | os.PathLike, optional
            Output file name.
        nodal_distance : {'line', 'orthogonal'}, default 'line'
            Method to calculate connection nodal distances:

             - 'line': distance between node and common face along connecting line
             (distance is not normal),
             - 'orthogonal': distance between node and its orthogonal projection onto
             common face (shortest distance).

        material_name : dict, optional
            Map of material names.
        gravity : ArrayLike, optional
            Gravity direction vector.
        incon : bool, default False
            If True, also export initial conditions.
        **kwargs : dict, optional
            Additional keyword arguments. See ``toughio.write_input`` for more details.

        Returns
        -------
        dict
            TOUGH mesh as a dict. Only provided if *filename* is None.

        """
        def dot(A: ArrayLike, B: ArrayLike) -> ArrayLike:
            """Calculate the dot product when arrays A and B have the same shape."""
            return (A * B).sum(axis=1)

        def intersection_line_plane(centers: ArrayLike, lines: ArrayLike, points: ArrayLike, normals: ArrayLike) -> ArrayLike:
            """Calculate the intersection point between a line and a plane."""
            tmp = dot(points - centers, normals) / dot(lines, normals)

            return centers + lines * tmp[:, None]

        def distance_point_plane(centers: ArrayLike, points: ArrayLike, normals: ArrayLike, mask: ArrayLike) -> ArrayLike:
            """Calculate the orthogonal distance of a point to a plane."""
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
        connections, face_centers, face_normals, face_areas = mesh._compute_connection_properties()
        labels_1 = labels[connections[:, 0]]
        labels_2 = labels[connections[:, 1]]
        centers_1 = centers[connections[:, 0]]
        centers_2 = centers[connections[:, 1]]
        bounds_1 = dirichlet[connections[:, 0]]
        bounds_2 = dirichlet[connections[:, 1]]

        # Direction vectors of connection lines
        lines = centers_2 - centers_1
        lines /= np.linalg.norm(lines, axis=1)[:, None]

        # Permeability directions
        mask = lines != 0.0
        permability_directions = np.where(mask.sum(axis=1) == 1, mask.argmax(axis=1) + 1, 1)

        # Nodal distances and gravity angles
        if nodal_distance == "line":
            fp = intersection_line_plane(centers_1, lines, face_centers, face_normals)
            distances_1 = np.where(bounds_1, 1.0e-9, np.linalg.norm(centers_1 - fp, axis=1))
            distances_2 = np.where(bounds_2, 1.0e-9, np.linalg.norm(centers_2 - fp, axis=1))
            angles = lines @ gravity

        elif nodal_distance == "orthogonal":
            distances_1 = distance_point_plane(centers_1, face_centers, face_normals, bounds_1)
            distances_2 = distance_point_plane(centers_2, face_centers, face_normals, bounds_2)
            angles = np.sign((face_normals * lines).sum(axis=1)) * (face_normals @ gravity)

        # Write MESH file
        # Elements
        elements = {
            label: {
                "material": (
                    material_name[material]
                    if material in material_name
                    else material
                ),
                "volume": volume,
                "center": center,
            }
            for label, material, volume, center in zip(labels, materials, volumes, centers)
            if label not in inactive_labels
        }

        # Connections
        connections = {}

        for l1, l2, isot, d1, d2, face_area, angle in zip(
            labels_1,
            labels_2,
            permability_directions,
            distances_1,
            distances_2,
            face_areas,
            angles,
        ):
            label = f"{l1}{l2}"

            if label in connections:
                connections[label]["nodal_distances"][0] = min(connections[label]["nodal_distances"][0], d1)
                connections[label]["nodal_distances"][1] = min(connections[label]["nodal_distances"][1], d2)
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

            for label, phi, k, index, values in zip(labels, porosities, permeabilities, phase_compositions, initial_conditions):
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

        if filename:
            write_input(filename, parameters, block="mesh", **kwargs)

            if incon:
                write_input(pathlib.Path(filename).parent / "INCON", parameters, block="incon", **kwargs)

        else:
            return parameters

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
        time_steps = np.asanyarray(time_steps) if time_steps is not None else np.arange(nt)

        if time_steps is not None and len(time_steps) != nt:
            raise ValueError(f"inconsitent number of data ({nt}) and time steps ({len(time_steps)})")

        # Convert to meshio
        mesh = pv.to_meshio(self.pyvista)
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
        nodal_distance: Literal["line", "orthogonal"] = "line",
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        incon: bool = False,
        **kwargs
    ) -> None:
        """
        Write mesh to TOUGH MESH file.

        Parameters
        ----------
        filename : str | os.PathLike, default 'MESH'
            Output file name.
        nodal_distance : {'line', 'orthogonal'}, default 'line'
            Method to calculate connection nodal distances:

             - 'line': distance between node and common face along connecting line
             (distance is not normal),
             - 'orthogonal': distance between node and its orthogonal projection onto
             common face (shortest distance).

        material_name : dict, optional
            Map of material names.
        gravity : ArrayLike, optional
            Gravity direction vector.
        incon : bool, default False
            If True, also export initial conditions to INCON file.
        **kwargs : dict, optional
            Additional keyword arguments. See ``toughio.write_input`` for more details.

        """
        self.to_tough(
            filename,
            nodal_distance,
            material_name,
            gravity,
            incon,
        )

    def write(self, filename: str | os.PathLike, file_format: Optional[str] = None) -> None:
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
            self.pyvista.save(filename)

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
        **kwargs
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
            p.set_scale(xscale, yscale, zscale)

        p.add_mesh(
            mesh,
            scalar_bar_args={
                "vertical": True,
                "position_y": 0.1,
                "height": 0.8,
            },
            **default_kwargs
        )

        if enable_picking:
            infos = p.add_text(
                "",
                position="upper_left",
                font_size=12,
                shadow=False,
            )

            def callback(mesh: pv.DataSet) -> None:
                i = mesh.cell_data["vtkOriginalCellIds"][0]
                label = self.labels[i]
                coords = np.round(mesh.get_cell(0).center, 3)
                material = self.materials[i]
                out = f"{label}\nCoords: ({', '.join(map(str, coords))})\nMaterial: {material}"

                infos.SetText(2, out)
                p.update()

            p.enable_element_picking(
                mode="cell",
                callback=callback,
                show_message=False,
                tolerance=tolerance,
                picker="cell",
            )

        p.add_axes()

        if parallel_projection:
            p.enable_parallel_projection()

        if plotter is None:
            p.show()

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

        mesh = mesh.cast_to_unstructured_grid()

        if tmp is not None:
            mesh.cell_data["vtkGhostType"] = tmp

        return mesh

    def _compute_connection_properties(self) -> tuple[ArrayLike, ArrayLike, ArrayLike, ArrayLike]:
        """Compute connection properties."""
        poly = (
            pvg.extract_cell_geometry(self.pyvista, remove_empty_cells=True)
            .compute_cell_sizes(length=True, area=True, volume=False)
        )
        mask = (poly["vtkOriginalCellIds"] >= 0).all(axis=1)
        connections = poly["vtkOriginalCellIds"][mask]
        centers = poly.cell_centers(vertex=False).points[mask]

        if self.ndim == 3:
            normals = poly.compute_normals(point_normals=False)["Normals"][mask]
            lengths_or_areas = poly["Area"][mask]

        else:
            normals = np.diff(
                poly.points[np.delete(poly.lines.reshape((poly.n_lines, 3)), 0, axis=1)],
                axis=1,
            ).squeeze()
            normals = np.column_stack((normals[:, 2], np.zeros(poly.n_lines), -normals[:, 0]))
            normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
            normals = normals[mask]
            lengths_or_areas = poly["Length"][mask]

        return connections, centers, normals, lengths_or_areas

    def _get_property(self, name: str, default: Optional[ArrayLike] = None) -> ArrayLike:
        """Get property data."""
        if name not in self.data:
            data = np.zeros(self.n_cells, dtype=float) if default is None else default
            self.add_data(name, data)

        return self.data[name]

    @property
    def active(self) -> ArrayLike:
        """Return active cell array."""
        return self._get_property("vtkGhostType", np.zeros(self.n_cells, dtype=np.uint8)) == 0

    @property
    def centers(self) -> ArrayLike:
        """Return cell center array."""
        # Ghost cells are converted to empty cells after casting which yield no center
        mesh = self._cast_to_unstructured_grid(self.pyvista)
        
        # Handle empty cells (that exists in the mesh but are not ghost cells)
        cell_centers = np.full((mesh.n_cells, 3), np.nan)
        cell_centers[mesh.celltypes != pv.CellType.EMPTY_CELL] = mesh.cell_centers(vertex=False).points

        return cell_centers

    @property
    def data(self) -> dict:
        """Return mesh data."""
        return self.pyvista.cell_data

    cell_data = data

    @property
    def dirichlet(self) -> ArrayLike:
        """Return Dirichlet cell array."""
        return self._get_property("Dirichlet", np.zeros(self.n_cells, dtype=bool))

    @dirichlet.setter
    def dirichlet(self, value: ArrayLike) -> None:
        """Set Dirichlet cell array."""
        self.add("Dirichlet", np.asanyarray(value).astype(bool))

    @property
    def initial_conditions(self) -> ArrayLike:
        """Return initial conditions array."""
        return self._get_property("Initial Conditions")

    @initial_conditions.setter
    def initial_conditions(self, value: ArrayLike) -> None:
        """Set initial conditions array."""
        self.add_data("Initial Conditions", np.asanyarray(value).astype(float))

    @property
    def labels(self) -> ArrayLike:
        """Return cell labels."""
        return np.asanyarray(self.metadata["Label"])

    @labels.setter
    def labels(self, value: ArrayLike) -> None:
        """Set cell labels."""
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
    def materials(self) -> ArrayLike:
        """Return cell materials. Always return a copy."""
        metadata = self.metadata

        try:
            material_map = {v: k for k, v in metadata[self.material_key].items()}

            return np.array(
                [
                    material_map[material]
                    if material in material_map
                    else material
                    for material in self.materials_digitized
                ]
            )

        except KeyError:
            return self.materials_digitized.copy()

    @property
    def materials_digitized(self) -> ArrayLike:
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
    def permeabilities(self) -> ArrayLike:
        """Return cell permeability array."""
        return self._get_property("Permeability")

    @permeabilities.setter
    def permeabilities(self, value: ArrayLike) -> None:
        """Set cell permeability array."""
        self.add_data("Permeability", np.asanyarray(value).astype(float))

    @property
    def phase_compositions(self) -> ArrayLike:
        """Return phase composition array."""
        return self._get_property("Phase Composition", np.zeros(self.n_cells, dtype=int))

    @phase_compositions.setter
    def phase_compositions(self, value: ArrayLike) -> None:
        """Set phase composition array."""
        self.add_data("Phase Composition", np.asanyarray(value).astype(int))

    @property
    def points(self) -> ArrayLike:
        """Return points array."""
        return self.pyvista.points

    @property
    def porosities(self) -> ArrayLike:
        """Return cell porosity array."""
        return self._get_property("Porosity")

    @porosities.setter
    def porosities(self, value: ArrayLike) -> None:
        """Set cell porosity array."""
        self.add_data("Porosity", np.asanyarray(value).astype(float))

    @property
    def pyvista(self) -> pv.StructuredGrid | pv.UnstructuredGrid:
        """Return underlying PyVista mesh."""
        return self._pyvista

    @property
    def volumes(self) -> ArrayLike:
        """Return cell volume array."""
        is3d = self.ndim == 3
        key = "Volume" if is3d else "Area"

        return np.abs(self.pyvista.compute_cell_sizes(length=False, area=not is3d, volume=is3d)[key])


class Mesh(BaseMesh):
    """
    Mesh class.
    
    Parameters
    ----------
    args : str | os.PathLike | GridLike | meshio.Mesh | toughio.Mesh | ArrayLike
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

    def extrude_to_3d(self, height: ArrayLike = 1.0, axis: int = 2) -> Mesh:
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

        return Mesh(extrude_to_3d(self.pyvista))

    def prune_duplicates(self) -> Mesh:
        """
        Delete duplicate points.

        Returns
        -------
        toughio.Mesh
            Mesh with duplicate points removed.

        """
        return Mesh(self.pyvista.clean(produce_merge_map=False))


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
        args : str | os.PathLike | GridLike | toughio.Mesh
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
                raise ValueError("could not initialize a cylindric mesh from an unstructured mesh")

            if self.pyvista.dimensions[1] != 1:
                raise ValueError("could not initialize a cylindric mesh from a non vertical mesh")

            if x.size * z.size != np.prod(self.pyvista.dimensions):
                raise ValueError("could not initialize a cylindric mesh from a non rectilinear mesh")

        self.points[:, 0] -= x[0]
        self.points[:, 1] = 0.0

    def __getitem__(self, key: tuple[int | slice | ArrayLike]) -> Self:
        """Slice a mesh."""
        if isinstance(key, int):
            return self.pyvista.get_cell(key)

        else:
            mesh = self.__class__(
                self._cast_to_unstructured_grid(self.pyvista).extract_cells(key),
                metadata=self.metadata,
                force=True,
            )
            mesh.labels = self.labels[key]

            return mesh

    def _compute_connection_properties(self) -> tuple[ArrayLike, ArrayLike, ArrayLike, ArrayLike]:
        """Compute connection properties."""
        connections, centers, normals, lengths = super()._compute_connection_properties()

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

        def get_radii(pipe: Pipe) -> tuple[float, float]:
            rout = pipe.radius + pipe.thickness
            rind = np.flatnonzero(x == rout)[0]
            rin = x[rind - 1] if rind else 0.0

            return rin, rout

        if not np.isin(well.radii, x).all():
            raise ValueError("could not generate wellbore with radius not matching radial discretization of porous medium")

        well_domain = np.full(self.n_cells, -1)
        cells_to_fuse = []

        for id_, pipe in zip(np.arange(len(well.pipes))[::-1], well.pipes[::-1]):
            mask = (
                (centers[:, 0] < pipe.radius + pipe.thickness)
                & (centers[:, 2] > pipe.zmin)
                & (centers[:, 2] < pipe.zmax)
            )
            self.set_material(pipe.material, mask)
            self.set_active(True, mask)

            if not pipe.is_porous:
                well_domain[mask] = id_
            
            # Find horizontally connected cells to be fused to ensure 1D vertical flow in wellbore
            pipe_centers = centers[mask]

            if not pipe.is_porous and np.ptp(pipe_centers[:, 0]) > 0.0:
                for z in np.unique(pipe_centers[:, 2]):
                    cells_to_fuse.append(np.flatnonzero(np.logical_and(mask, centers[:, 2] == z)))

        self.add_data("WellDomain", well_domain)

        # Fuse cells (this will change the mesh to an unstructured grid)
        # Only fuse cells with the same material ID
        cells_to_fuse = [
            ids for ids in cells_to_fuse
            if np.ptp(self.materials_digitized[ids]) == 0
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
                key = (min(id1, id2), max(id1, id2))

            # Well-formation connection
            else:
                key = id1

            connections[key] = {
                "type": connection["type"],
                "zmin": connection["zmin"],
                "zmax": connection["zmax"],
            }

        if connections:
            self.metadata["WellConnection"] = connections

        # Wellheads
        for wellhead in well.wellheads:
            whid = self.find_nearest_cell((wellhead.radius, 0.0, wellhead.zmax), material=wellhead.material)
            self.set_label(f"*{self.labels[whid][1:]}", whid)

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

    def to_tough(
        self,
        filename: Optional[str | os.PathLike] = None,
        nodal_distance: Literal["line", "orthogonal"] = "orthogonal",
        material_name: Optional[dict] = None,
        gravity: Optional[ArrayLike] = None,
        incon: bool = False,
        **kwargs
    ) -> dict | None:
        """
        Convert mesh to TOUGH mesh.

        Parameters
        ----------
        filename : str | os.PathLike, optional
            Output file name.
        nodal_distance : {'line', 'orthogonal'}, default 'orthogonal'
            Method to calculate connection nodal distances:

             - 'line': distance between node and common face along connecting line
             (distance is not normal),
             - 'orthogonal': distance between node and its orthogonal projection onto
             common face (shortest distance).

        material_name : dict, optional
            Map of material names.
        gravity : ArrayLike, optional
            Gravity direction vector.
        incon : bool, default False
            If True, also export initial conditions.
        **kwargs : dict, optional
            Additional keyword arguments. See ``toughio.write_input`` for more details.

        Returns
        -------
        dict
            TOUGH mesh as a dict. Only provided if *filename* is None.

        """
        parameters = super().to_tough(
            filename=filename,
            nodal_distance=nodal_distance,
            material_name=material_name,
            gravity=gravity,
            incon=incon,
            **kwargs
        )
        well_domain = self.data.get("WellDomain", np.full(self.n_cells, -1))

        if (well_domain >= 0).any():
            label_length = self.label_length
            label_map = {label: i for i, label in enumerate(self.labels)}
            well_connections = self.metadata.get("WellConnection", {})
            well_isots = {
                "well": {"branch": 3, "heat": -1, "forward": 4, "backward": 5},
                "formation": {"heat": -1, "perforation": 1, "gas": 4, "liquid": 5, "backward": 6},
            }

            # Update connections
            connections = {}

            for k, v in parameters["connections"].items():
                l1, l2 = k[:label_length], k[label_length:]
                i1, i2 = label_map[l1], label_map[l2]
                wid1, wid2 = well_domain[i1], well_domain[i2]

                # Well connections
                if (wid1 >= 0 or wid2 >= 0):
                    # Well-well connection
                    if (min(wid1, wid2), max(wid1, wid2)) in well_connections:
                        key = "well"
                        connection = well_connections[(min(wid1, wid2), max(wid1, wid2))]

                    # Well-formation connection
                    elif wid1 in well_connections or wid2 in well_connections:
                        key = "formation"

                        try:
                            connection = well_connections[wid1]

                        except KeyError:
                            connection = well_connections[wid2]

                    else:
                        connection = None

                    # Horizontal connections
                    if v["gravity_cosine_angle"] == 0.0:
                        # Update ISOT
                        isot = -1

                        if connection:
                            zmin, zmax = connection["zmin"], connection["zmax"]
                            z1 = parameters["elements"][l1]["center"][2]
                            z2 = parameters["elements"][l2]["center"][2]
                            type_ = connection["type"]

                            if zmin <= z1 <= zmax and zmin <= z2 <= zmax:
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
                        if connection and connection["type"] == "none":
                            continue

                connections[k] = v

            parameters["connections"] = connections

        return parameters

    @property
    def volumes(self) -> ArrayLike:
        """Return cell volume array."""
        get_min_max = lambda arr: (arr.min(), arr.max())
        cells = pvg.get_cell_connectivity(self._cast_to_unstructured_grid(self.pyvista))
        xmin, xmax = np.transpose([get_min_max(self.points[:, 0][cell]) for cell in cells])
        zmin, zmax = np.transpose([get_min_max(self.points[:, 2][cell]) for cell in cells])
        
        return np.pi * (xmax ** 2 - xmin ** 2) * (zmax - zmin)
