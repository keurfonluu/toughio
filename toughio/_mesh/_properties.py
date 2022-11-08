import logging
from itertools import chain

import numpy as np


def _materials(mesh):
    """Return materials of cell in mesh."""
    if "material" in mesh.cell_data:
        if mesh.field_data:
            out = mesh.cell_data["material"]
            try:
                field_data_dict = {v[0]: k for k, v in mesh.field_data.items()}
                out = [field_data_dict[mat] for mat in out]
            except KeyError:
                logging.warning(
                    (
                        "field_data is not defined for all materials. "
                        "Returns materials as integers."
                    )
                )
                out = mesh.cell_data["material"]
        else:
            out = mesh.cell_data["material"]
    else:
        out = np.ones(mesh.n_cells, dtype=int)

    return np.asarray(out)


def _faces(mesh):
    """Return connectivity of faces of cell in mesh."""
    meshio_type_to_faces = {
        "tetra": {
            "triangle": np.array([[1, 2, 3], [0, 3, 2], [0, 1, 3], [0, 2, 1]]),
        },
        "pyramid": {
            "triangle": np.array([[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]),
            "quad": np.array([[0, 3, 2, 1]]),
        },
        "wedge": {
            "triangle": np.array([[0, 2, 1], [3, 4, 5]]),
            "quad": np.array([[0, 1, 4, 3], [1, 2, 5, 4], [0, 3, 5, 2]]),
        },
        "hexahedron": {
            "quad": np.array(
                [
                    [0, 3, 2, 1],
                    [4, 5, 6, 7],
                    [0, 1, 5, 4],
                    [1, 2, 6, 5],
                    [2, 3, 7, 6],
                    [0, 4, 7, 3],
                ]
            ),
        },
    }

    return [
        [c[v] for v in meshio_type_to_faces[cell.type].values()]
        for cell in mesh.cells
        for c in cell.data
    ]


def _face_normals(mesh):
    """Return normal vectors of faces in mesh."""
    faces_dict, faces_cell, _ = _get_faces(_faces(mesh))

    # Face normal vectors
    normals = np.concatenate(
        [_get_triangle_normals(mesh, v) for k, v in faces_dict.items()]
    )
    normals_mag = np.linalg.norm(normals, axis=-1)
    normals /= normals_mag[:, None]

    # Reorganize outputs
    face_normals = [[] for _ in range(mesh.n_cells)]
    iface = np.concatenate([v for v in faces_cell.values()])
    for i, normal in zip(iface, normals):
        face_normals[i].append(normal)

    return face_normals


def _face_areas(mesh):
    """Return areas of faces in mesh."""
    faces_dict, faces_cell, _ = _get_faces(_faces(mesh))

    # Face areas
    areas = np.concatenate(
        [_get_triangle_normals(mesh, v) for k, v in faces_dict.items()]
    )
    areas = np.linalg.norm(areas, axis=-1)
    if "quad" in faces_dict and len(faces_dict["quad"]):
        tmp = np.concatenate(
            [
                _get_triangle_normals(mesh, v, [0, 2, 3])
                if k == "quad"
                else np.zeros((len(v), 3))
                for k, v in faces_dict.items()
            ]
        )
        areas += np.linalg.norm(tmp, axis=-1)
    areas *= 0.5

    # Reorganize outputs
    face_areas = [[] for _ in range(mesh.n_cells)]
    iface = np.concatenate([v for v in faces_cell.values()])
    for i, area in zip(iface, areas):
        face_areas[i].append(area)

    return [np.array(face) for face in face_areas]


def _volumes(mesh):
    """Return volumes of cell in mesh."""
    meshio_type_to_tetra = {
        "tetra": np.array([[0, 1, 2, 3]]),
        "pyramid": np.array([[0, 1, 3, 4], [1, 2, 3, 4]]),
        "wedge": np.array([[0, 1, 2, 5], [0, 1, 4, 5], [0, 3, 4, 5]]),
        "hexahedron": np.array(
            [[0, 1, 3, 4], [1, 4, 5, 6], [1, 2, 3, 6], [3, 4, 6, 7], [1, 3, 4, 6]]
        ),
    }

    out = []
    for cell in mesh.cells:
        tetras = np.vstack([c[meshio_type_to_tetra[cell.type]] for c in cell.data])
        tetras = mesh.points[tetras]
        out.append(
            np.sum(
                np.split(
                    np.abs(
                        _scalar_triple_product(
                            tetras[:, 1] - tetras[:, 0],
                            tetras[:, 2] - tetras[:, 0],
                            tetras[:, 3] - tetras[:, 0],
                        )
                    ),
                    len(cell.data),
                ),
                axis=1,
            )
            / 6.0
        )
    return np.concatenate(out)


def _connections(mesh):
    """
    Return mesh connections.

    Assume conformity and that points and cells are uniquely defined in mesh.

    """
    if np.shape(mesh.points)[1] != 3:
        raise ValueError("Connections for 2D mesh has not been implemented yet.")

    faces_dict, faces_cell, faces_index = _get_faces(_faces(mesh))
    faces_dict = {k: np.sort(np.vstack(v), axis=1) for k, v in faces_dict.items()}

    # Prune duplicate faces
    uf, tmp1, tmp2 = {}, {}, {}
    for k, v in faces_dict.items():
        up, uf[k] = np.unique(v, axis=0, return_inverse=True)
        tmp1[k] = [[] for _ in range(len(up))]
        tmp2[k] = [[] for _ in range(len(up))]

    # Make connections
    for k, v in uf.items():
        for i, j in enumerate(v):
            tmp1[k][j].append(faces_cell[k][i])
            tmp2[k][j].append(faces_index[k][i])
    conne = [vv for v in tmp1.values() for vv in v if len(vv) == 2]
    iface = [vv for v in tmp2.values() for vv in v if len(vv) == 2]

    # Reorganize output
    out = np.full((mesh.n_cells, 6), -1)
    for (i1, i2), (j1, j2) in zip(conne, iface):
        out[i1, j1] = i2
        out[i2, j2] = i1

    return out


def _qualities(mesh):
    """Return quality of cells as a measure of the orthogonality of its connections."""
    nodes = mesh.centers
    connections = mesh.connections
    face_normals = mesh.face_normals

    cell_list = set()
    centers, int_normals, mapper = [], [], []
    for i, connection in enumerate(connections):
        for iface, j in enumerate(connection):
            if j >= 0 and j not in cell_list:
                centers.append([nodes[i], nodes[j]])
                int_normals.append(face_normals[i][iface])
                mapper.append((i, j))

        cell_list.add(i)

    int_normals = np.array(int_normals)
    lines = np.diff(centers, axis=1)[:, 0]
    lines /= np.linalg.norm(lines, axis=1)[:, None]
    angles = np.abs((lines * int_normals).sum(axis=1))

    # Reorganize output
    out = [[] for _ in range(mesh.n_cells)]
    for (i, j), angle in zip(mapper, angles):
        out[i].append(angle)
        out[j].append(angle)

    return out


def _get_faces(faces):
    """Return dictionary of faces."""
    faces_dict = {"triangle": [], "quad": []}
    faces_cell = {"triangle": [], "quad": []}
    faces_index = {"triangle": [], "quad": []}
    numvert_to_face_type = {3: "triangle", 4: "quad"}

    for i, face in enumerate(faces):
        for j, f in enumerate(chain.from_iterable(face)):
            n = len(f)
            face_type = numvert_to_face_type[n]
            faces_dict[face_type].append(f[:n])
            faces_cell[face_type].append(i)
            faces_index[face_type].append(j)

    # Stack arrays or remove empty cells
    faces_dict = {k: np.vstack(v) for k, v in faces_dict.items() if len(v)}
    faces_cell = {k: v for k, v in faces_cell.items() if len(v)}
    faces_index = {k: v for k, v in faces_index.items() if len(v)}

    return faces_dict, faces_cell, faces_index


def _get_triangle_normals(mesh, faces, islice=None):
    """Calculate normal vectors of triangular faces."""
    islice = islice if islice is not None else [0, 1, 2]

    triangles = np.vstack([c[islice] for c in faces])
    triangles = mesh.points[triangles]

    return _cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])


def _cross(a, b):
    """Calculate cross product (faster than :func:`np.cross`)."""
    return a[:, [1, 2, 0]] * b[:, [2, 0, 1]] - a[:, [2, 0, 1]] * b[:, [1, 2, 0]]


def _scalar_triple_product(a, b, c):
    """Calculate determinant as scalar triple product."""
    return (a * _cross(b, c)).sum(axis=-1)
