import logging
import os

import numpy as np

from ..._common import open_file
from ._helpers import block

__all__ = [
    "read",
    "write",
]


def read(filename, label_length=None):
    """Read TOUGH MESH file."""
    from ... import read_input

    mesh = read_input(filename, file_format="tough", label_length=label_length)
    return {
        k: v
        for k, v in mesh.items()
        if k
        in {
            "elements",
            "elements_order",
            "coordinates",
            "connections",
            "connections_order",
            "initial_conditions",
            "initial_conditions_order",
        }
    }


def write(
    filename,
    mesh,
    nodal_distance="line",
    material_name=None,
    material_end=None,
    incon=False,
    coord=False,
    eos=None,
    gravity=None,
):
    """Write TOUGH MESH file (and INCON file)."""
    if nodal_distance not in {"line", "orthogonal"}:
        raise ValueError()
    if not (material_name is None or isinstance(material_name, dict)):
        raise TypeError()
    if not (material_end is None or isinstance(material_end, (str, list, tuple))):
        raise TypeError()
    if not isinstance(incon, bool):
        raise TypeError()
    if not (gravity is None or (np.ndim(gravity) == 1 and len(gravity) == 3)):
        raise ValueError()

    # Required variables for blocks ELEME and CONNE
    num_cells = mesh.n_cells
    labels = mesh.labels
    nodes = mesh.centers
    materials = mesh.materials
    volumes = mesh.volumes
    boundary_conditions = (
        mesh.cell_data["boundary_condition"]
        if "boundary_condition" in mesh.cell_data
        else np.zeros(num_cells, dtype=int)
    )
    points = mesh.points
    connections = mesh.connections
    gravity = gravity if gravity is not None else np.array([0.0, 0.0, -1.0])

    # Define parameters related to faces
    faces = mesh.faces
    face_normals = mesh.face_normals
    face_areas = mesh.face_areas

    # Required variables for block INCON
    primary_variables, porosities, permeabilities, phase_compositions = init_incon(mesh)
    incon = check_incon(
        incon,
        primary_variables,
        porosities,
        permeabilities,
        phase_compositions,
        num_cells,
        eos,
    )

    # Write MESH file
    write_mesh(
        filename,
        num_cells,
        labels,
        nodes,
        materials,
        volumes,
        boundary_conditions,
        points,
        connections,
        gravity,
        faces,
        face_normals,
        face_areas,
        nodal_distance,
        material_name,
        material_end,
        coord,
    )

    # Write INCON file
    if incon:
        head = os.path.split(filename)[0]
        write_incon(
            os.path.join(head, "INCON") if head else "INCON",
            labels,
            primary_variables,
            porosities,
            permeabilities,
            phase_compositions,
            eos,
        )


def check_incon(
    incon,
    primary_variables,
    porosities,
    permeabilities,
    phase_compositions,
    num_cells,
    eos,
):
    """Check INCON inputs and show warnings if necessary."""
    do_incon = incon
    if incon and (primary_variables == -1.0e9).all():
        logging.warning("Initial conditions are not defined. Skipping INCON.")
        do_incon = False

    cond = np.logical_and(
        primary_variables[:, 0] > -1.0e9,
        primary_variables[:, 0] < 0.0,
    )
    if cond.any():
        logging.warning("Negative pore pressures found in 'INCON'.")

    if porosities is not None:
        if not incon:
            logging.warning("Porosity is only exported if incon is provided.")
        else:
            if not (len(porosities) == num_cells and porosities.ndim == 1):
                raise ValueError("Inconsistent porosity array.")

    if permeabilities is not None:
        if not incon:
            logging.warning(
                "Permeability modifiers are only exported if incon is provided."
            )
        else:
            if permeabilities.ndim not in {1, 2}:
                raise ValueError()
            if not (
                permeabilities.shape == (num_cells, 3)
                if permeabilities.ndim == 2
                else len(permeabilities) == num_cells
            ):
                raise ValueError("Inconsistent permeability modifiers array.")

    if eos == "tmvoc" and phase_compositions is not None:
        if not incon:
            logging.warning("Phase composition is only exported if incon is provided.")
        else:
            if not (
                len(phase_compositions) == num_cells and phase_compositions.ndim == 1
            ):
                raise ValueError("Inconsistent phase composition array.")

    return do_incon


def write_mesh(
    filename,
    num_cells,
    labels,
    nodes,
    materials,
    volumes,
    boundary_conditions,
    points,
    connections,
    gravity,
    faces,
    face_normals,
    face_areas,
    nodal_distance,
    material_name,
    material_end,
    coord,
):
    """Write MESH file."""
    # Check materials
    materials = [
        f"{material.strip():5}" if isinstance(material, str) else material
        for material in materials
    ]
    material_name = material_name if material_name else {}
    material_end = material_end if material_end else []
    material_end = [material_end] if isinstance(material_end, str) else material_end

    with open_file(filename, "w") as f:
        _write_eleme(
            f,
            labels,
            nodes,
            materials,
            volumes,
            boundary_conditions,
            material_name,
            material_end,
        )

        if coord:
            _write_coord(
                f,
                nodes,
                materials,
                material_end,
            )

        _write_conne(
            f,
            labels,
            nodes,
            points,
            connections,
            gravity,
            boundary_conditions,
            faces,
            face_normals,
            face_areas,
            nodal_distance,
        )


def write_incon(
    filename,
    labels,
    primary_variables,
    porosities,
    permeabilities,
    phase_compositions,
    eos,
):
    """Write INCON file."""
    with open_file(filename, "w") as f:
        _write_incon(
            f,
            labels,
            primary_variables,
            porosities,
            permeabilities,
            phase_compositions,
            eos,
        )


@block("ELEME")
def _write_eleme(
    f,
    labels,
    nodes,
    materials,
    volumes,
    boundary_conditions,
    material_name,
    material_end,
):
    """Write ELEME block."""
    from ._helpers import _write_eleme as writer

    # Apply time-independent Dirichlet boundary conditions
    volumes[boundary_conditions.astype(bool)] *= 1.0e50

    # Write ELEME block
    ending = []
    iterables = zip(materials, writer(labels, materials, volumes, nodes, material_name))
    for material, record in iterables:
        if material not in material_end:
            f.write(record)
        else:
            ending.append(record)

    # Append ending cells at the end of the block
    if material_end:
        for record in ending:
            f.write(record)


@block("COORD")
def _write_coord(
    f,
    nodes,
    materials,
    material_end,
):
    """Write COORD block."""
    from ._helpers import _write_coord as writer

    # Write COORD block
    ending = []
    for material, record in zip(materials, writer(nodes)):
        if material not in material_end:
            f.write(record)
        else:
            ending.append(record)

    # Append ending cells at the end of the block
    if material_end:
        for record in ending:
            f.write(record)


@block("CONNE")
def _write_conne(
    f,
    labels,
    nodes,
    points,
    connections,
    gravity,
    boundary_conditions,
    faces,
    face_normals,
    face_areas,
    nodal_distance,
):
    """Write CONNE block."""
    from ._helpers import _write_conne as writer

    # Define unique connection variables
    cell_list = set()
    clabels, centers, int_points, int_normals, areas, bounds = [], [], [], [], [], []
    for i, connection in enumerate(connections):
        if (connection >= 0).any():
            for iface, j in enumerate(connection):
                if j >= 0 and j not in cell_list:
                    # Label
                    clabels.append((labels[i], labels[j]))

                    # Nodal points
                    centers.append([nodes[i], nodes[j]])

                    # Common interface defined by single point and normal vector
                    face = faces[i, iface]
                    int_points.append(points[face[face >= 0][0]])
                    int_normals.append(face_normals[i][iface])

                    # Area of common face
                    areas.append(face_areas[i][iface])

                    # Boundary conditions
                    bounds.append((boundary_conditions[i], boundary_conditions[j]))
        else:
            logging.warning(f"Element '{labels[i]}' is not connected to the grid.")
        cell_list.add(i)

    centers = np.array(centers)
    int_points = np.array(int_points)
    int_normals = np.array(int_normals)
    bounds = np.array(bounds)

    # Calculate remaining variables
    lines = np.diff(centers, axis=1)[:, 0]
    isot = _isot(lines)
    angles = np.dot(lines, gravity) / np.linalg.norm(lines, axis=1)

    if nodal_distance == "line":
        fp = _intersection_line_plane(centers[:, 0], lines, int_points, int_normals)
        d1 = np.where(bounds[:, 0], 1.0e-9, np.linalg.norm(centers[:, 0] - fp, axis=1))
        d2 = np.where(bounds[:, 1], 1.0e-9, np.linalg.norm(centers[:, 1] - fp, axis=1))
    elif nodal_distance == "orthogonal":
        d1 = _distance_point_plane(centers[:, 0], int_points, int_normals, bounds[:, 0])
        d2 = _distance_point_plane(centers[:, 1], int_points, int_normals, bounds[:, 1])

    # Write CONNE block
    for line in writer(clabels, isot, d1, d2, areas, angles):
        f.write(line)


@block("INCON")
def _write_incon(
    f, labels, primary_variables, porosities, permeabilities, phase_compositions, eos
):
    """Write INCON block."""
    from ._helpers import _write_incon as writer

    # Write INCON block
    if permeabilities is not None:
        permeabilities = (
            permeabilities[:, None] if permeabilities.ndim == 1 else permeabilities
        )

    for record in writer(
        labels, primary_variables, porosities, permeabilities, phase_compositions, eos
    ):
        f.write(record)


def init_incon(mesh):
    """Initialize primary variables, porosity and permeability arrays."""
    primary_variables = (
        mesh.cell_data["initial_condition"]
        if "initial_condition" in mesh.cell_data
        else np.full((mesh.n_cells, 4), -1.0e9)
    )
    porosities = mesh.cell_data["porosity"] if "porosity" in mesh.cell_data else None
    permeabilities = (
        mesh.cell_data["permeability"] if "permeability" in mesh.cell_data else None
    )
    phase_compositions = (
        mesh.cell_data["phase_composition"]
        if "phase_composition" in mesh.cell_data
        else None
    )

    return primary_variables, porosities, permeabilities, phase_compositions


def _intersection_line_plane(center, lines, int_points, int_normals):
    """
    Calculate the intersection point between a line and a plane.

    Calculate intersection between a line defined by a point and a direction vector and
    a plane defined by one point and a normal vector.

    """
    tmp = _dot(int_points - center, int_normals) / _dot(lines, int_normals)
    return center + lines * tmp[:, None]


def _distance_point_plane(center, int_points, int_normals, mask):
    """
    Calculate orthogonal distance.

    Calculate orthogonal distance of a point to a plane defined by one point and a
    normal vector.

    """
    return np.where(mask, 1.0e-9, np.abs(_dot(center - int_points, int_normals)))


def _isot(lines):
    """
    Determine direction of anisotropy.

    Given the direction of the line connecting the cell centers, calculate the
    direction of anisotropy.

    Note
    ----
    It always returns 1 if the connection line is not colinear with X, Y or Z.

    """
    mask = lines != 0.0
    return np.where(mask.sum(axis=1) == 1, mask.argmax(axis=1) + 1, 1)


def _dot(A, B):
    """Calculate dot product when arrays A and B have the same shape."""
    return (A * B).sum(axis=1)
