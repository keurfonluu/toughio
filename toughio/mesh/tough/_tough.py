from __future__ import division, unicode_literals, with_statement

import logging

import numpy

__all__ = [
    "read",
    "write",
]


def block(keyword):
    """Decorate block writing functions."""

    def decorator(func):
        from functools import wraps

        header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"

        @wraps(func)
        def wrapper(f, *args):
            f.write("{}{}\n".format(keyword, header))
            func(f, *args)
            f.write("\n")

        return wrapper

    return decorator


def read(filename):
    """
    Read TOUGH MESH file is not supported yet.

    MESH file does not store any geometrical information except node centers.

    """
    raise NotImplementedError("Reading TOUGH MESH file is not supported.")


def write(filename, mesh, nodal_distance, material_name, material_end, incon):
    """Write TOUGH MESH file."""
    if nodal_distance not in {"line", "orthogonal"}:
        raise ValueError()
    if not (material_name is None or isinstance(material_name, dict)):
        raise TypeError()
    if not (material_end is None or isinstance(material_end, (str, list, tuple))):
        raise TypeError()
    if not isinstance(incon, bool):
        raise TypeError()

    # Required variables for blocks ELEME and CONNE
    num_cells = mesh.n_cells
    labels = mesh.labels
    nodes = mesh.centers
    materials = mesh.materials
    volumes = mesh.volumes
    boundary_conditions = (
        mesh.cell_data["boundary_condition"]
        if "boundary_condition" in mesh.cell_data.keys()
        else numpy.zeros(num_cells, dtype=int)
    )
    points = mesh.points
    connections = mesh.connections
    gravity = numpy.array([0.0, 0.0, -1.0])

    # Define parameters related to faces
    faces = mesh.faces
    face_normals = mesh.face_normals
    face_areas = mesh.face_areas

    # Required variables for block INCON
    primary_variables = None
    porosities = None
    permeabilities = None
    if incon:
        primary_variables = (
            mesh.cell_data["initial_condition"]
            if "initial_condition" in mesh.cell_data.keys()
            else primary_variables
        )
        porosities = (
            mesh.cell_data["porosity"]
            if "porosity" in mesh.cell_data.keys()
            else porosities
        )
        permeabilities = (
            mesh.cell_data["permeability"]
            if "permeability" in mesh.cell_data.keys()
            else permeabilities
        )

    # Write MESH and INCON files
    write_buffer(
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
        primary_variables,
        porosities,
        permeabilities,
        nodal_distance,
        material_name,
        material_end,
        incon,
    )


def write_buffer(
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
    primary_variables,
    porosities,
    permeabilities,
    nodal_distance,
    material_name,
    material_end,
    incon,
):
    materials = [
        "{:5}".format(material.strip()) if isinstance(material, str) else material
        for material in materials
    ]
    material_name = material_name if material_name else {}
    material_end = material_end if material_end else []
    material_end = [material_end] if isinstance(material_end, str) else material_end

    # Check INCON inputs and show warnings if necessary
    if incon and primary_variables is None:
        logging.warning(
            ("Initial conditions are not defined. " "Writing INCON will be ignored.")
        )

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

    # Write MESH file
    with open(filename, "w") as f:
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

    # Write INCON file
    if incon and primary_variables is not None:
        import os

        head = os.path.split(filename)[0]
        filename = os.path.join(head, "INCON") if head else "INCON"
        with open(filename, "w") as f:
            _write_incon(
                f, labels, primary_variables, porosities, permeabilities,
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
    # Apply time-independent Dirichlet boundary conditions
    volumes *= numpy.where(boundary_conditions, 1.0e50, 1.0)

    # Write ELEME block
    fmt = "{:5.5}{:>5}{:>5}{:>5}{:10.4e}{:>10}{:>10}{:10.3e}{:10.3e}{:10.3e}\n"
    ending = []
    iterables = zip(labels, materials, volumes, nodes)
    for label, material, volume, node in iterables:
        mat = material_name[material] if material in material_name.keys() else material
        record = fmt.format(
            label,  # ID
            "",  # NSEQ
            "",  # NADD
            mat,  # MAT
            volume,  # VOLX
            "",  # AHTX
            "",  # PMX
            node[0],  # X
            node[1],  # Y
            node[2],  # Z
        )
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
    # Define unique connection variables
    cell_list = set()
    clabels, centers, int_points, int_normals, areas, bounds = [], [], [], [], [], []
    for i, connection in enumerate(connections):
        if (connection >= 0).any():
            for iface, j in enumerate(connection):
                if j >= 0 and j not in cell_list:
                    # Label
                    clabels.append("{:5.5}{:5.5}".format(labels[i], labels[j]))

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
            logging.warning(
                "Element '{}' is not connected to the grid.".format(labels[i])
            )
        cell_list.add(i)

    centers = numpy.array(centers)
    int_points = numpy.array(int_points)
    int_normals = numpy.array(int_normals)
    bounds = numpy.array(bounds)

    # Calculate remaining variables
    lines = numpy.diff(centers, axis=1)[:, 0]
    isot = _isot(lines)
    angles = numpy.dot(lines, gravity) / numpy.linalg.norm(lines, axis=1)

    if nodal_distance == "line":
        fp = _intersection_line_plane(centers[:, 0], lines, int_points, int_normals)
        d1 = numpy.where(
            bounds[:, 0], 1.0e-9, numpy.linalg.norm(centers[:, 0] - fp, axis=1)
        )
        d2 = numpy.where(
            bounds[:, 1], 1.0e-9, numpy.linalg.norm(centers[:, 1] - fp, axis=1)
        )
    elif nodal_distance == "orthogonal":
        d1 = _distance_point_plane(centers[:, 0], int_points, int_normals, bounds[:, 0])
        d2 = _distance_point_plane(centers[:, 1], int_points, int_normals, bounds[:, 1])

    # Write CONNE block
    fmt = "{:10.10}{:>5}{:>5}{:>5}{:>5g}{:10.4e}{:10.4e}{:10.4e}{:10.3e}\n"
    iterables = zip(clabels, isot, d1, d2, areas, angles)
    for label, isot, d1, d2, area, angle in iterables:
        record = fmt.format(
            label,  # ID1-ID2
            "",  # NSEQ
            "",  # NAD1
            "",  # NAD2
            isot,  # ISOT
            d1,  # D1
            d2,  # D2
            area,  # AREAX
            angle,  # BETAX
        )
        f.write(record)


@block("INCON")
def _write_incon(f, labels, primary_variables, porosities, permeabilities):
    """Write INCON block."""
    # Check initial pore pressures
    cond = numpy.logical_and(
        primary_variables[:, 0] > -1.0e9, primary_variables[:, 0] < 0.0,
    )
    if cond.any():
        logging.warning("Negative pore pressures found in 'INCON'.")

    # Write label, porosity and permeability
    buffer = ["{:5.5}".format(label) for label in labels]

    if porosities is not None:
        buffer = [
            buf + "{:10}{:15.9e}".format("", phi)
            for buf, phi in zip(buffer, porosities)
        ]
    else:
        buffer = [buf + "{:10}{:15}".format("", "") for buf in buffer]

    if permeabilities is not None:
        if permeabilities.ndim == 1:
            buffer = [
                buf + "{:10.3e}{:10}{:10}".format(k, "", "")
                for buf, k in zip(buffer, permeabilities)
            ]
        else:
            buffer = [
                buf + "{:10.3e}{:10.3e}{:10.3e}".format(*k)
                for buf, k in zip(buffer, permeabilities)
            ]
    else:
        buffer = [buf + "{:10}{:10}{:10}".format("", "", "") for buf in buffer]

    # Write INCON block
    for pvar, buf in zip(primary_variables, buffer):
        if (pvar > -1.0e9).any():
            f.write(buf + "\n")
            for v in pvar:
                f.write("{:20.4e}".format(v) if v > -1.0e9 else "{:20}".format(""))
            f.write("\n")


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
    return numpy.where(mask, 1.0e-9, numpy.abs(_dot(center - int_points, int_normals)))


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
    return numpy.where(mask.sum(axis=1) == 1, mask.argmax(axis=1) + 1, 1)


def _dot(A, B):
    """Calculate dot product when arrays A and B have the same shape."""
    return (A * B).sum(axis=1)
