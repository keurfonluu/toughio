# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from __future__ import division, with_statement, unicode_literals

import logging
import numpy as np
from .spatial import (
    cell_area,
    cell_volume,
    intersection_line_plane,
    distance_point_point,
)
from .utils import build_connectivity

__all__ = [
    "read",
    "write",
]


def read(filename):
    """
    Read TOUGH MESH file is not supported yet. MESH file does not store
    any geometrical information except node centers.
    """
    raise NotImplementedError(
        "Reading TOUGH MESH file is not supported."
    )


def write(filename, mesh, rotation_angle, leaf_size, n_jobs):
    """
    Write TOUGH MESH file.
    """
    labels = _labeler(mesh)
    with open(filename, "w") as f:
        header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"
        f.write("{}{}\n".format("ELEME", header))
        _write_eleme(f, mesh, labels)
        f.write("\n")
        f.write("{}{}\n".format("CONNE", header))
        _write_conne(f, mesh, labels, rotation_angle, leaf_size, n_jobs)


def _labeler(mesh):
    """
    Create five-character long element labels following:
    - 1st: from A to Z
    - 2nd and 3rd: from 1 to 9 then A to Z
    - 4th and 5th: from 00 to 99
    Increment is performed from right to left.
    """
    from string import ascii_uppercase
    alpha = list(ascii_uppercase)
    numer = [ "{:0>2}".format(i) for i in range(100) ]
    nomen = [ "{:1}".format(i+1) for i in range(9) ] + alpha

    out, i = {}, 0
    for k, v in mesh.cells.items():
        out[k] = []
        for _ in v:
            q1, r1 = divmod(i, len(numer))
            q2, r2 = divmod(q1, len(nomen))
            q3, r3 = divmod(q2, len(nomen))
            _, r4 = divmod(q3, len(nomen))
            out[k].append("".join([ alpha[r4], nomen[r3], nomen[r2], numer[r1] ]))
            i += 1
    return out


def _write_eleme(f, mesh, labels):
    """
    Write ELEME block.
    """
    rocks = _translate_rocks(mesh)
    fmt = "{:5.5}{:>5}{:>5}{:5.5}{:10.4e}{:10.4e}{:10.3e}{:10.3e}{:10.3e}{:10.3e}\n"

    inactive = []
    for k, v in mesh.cells.items():
        for i, corner in enumerate(v):
            points = mesh.points[corner]
            volume = cell_volume(points, meshio_type = k)
            x, y, z = points.mean(axis = 0)
            record = fmt.format(
                labels[k][i],               # ID
                "",                         # NSEQ
                "",                         # NADD
                rocks[k][i],                # MAT
                volume,                     # VOLX
                0.,                         # AHTX
                -1.,                        # PMX
                x,                          # X
                y,                          # Y
                z,                          # Z
            )
            if volume:
                f.write(record)
            else:
                inactive.append(record)

    # Disable zero volume boundary blocks by writing at the end of ELEME
    for record in inactive:
        f.write(record)


def _translate_rocks(mesh):
    """
    Convert meshio cell_data to material for ELEME block. 'tough:rock'
    keyword in cell_data is used to assign element material.
    """
    if mesh.cell_data and all([ "tough:rock" in mesh.cell_data[k].keys() for k in mesh.cells.keys() ]):
        rocks = { k: mesh.cell_data[k]["tough:rock"] for k in mesh.cells.keys() }
        if mesh.field_data:
            rock_names = {
                v[0]: k for k, v in mesh.field_data.items() if v[1] == 3
            }
            return { k: [ rock_names[vv] for vv in v ] for k, v in rocks.items() }
        else:
            return { k: [ str(int(vv)) for vv in v ] for k, v in rocks.items() }
    else:
        logging.warning(
            "'tough:rock' not found in cell_data. All cells assumed in the same rock group."
        )
        return { k: [ "    1" ]*len(v) for k, v in mesh.cells.items() }


def _write_conne(f, mesh, labels, rotation_angle, leaf_size, n_jobs):
    """
    Write CONNE block.
    """
    conn = build_connectivity(mesh, leaf_size, n_jobs)
    fmt = "{:5.5}{:5.5}{:>5}{:>5}{:>5}{:>5g}{:10.4e}{:10.4e}{:10.4e}{:10.3e}\n"

    # Loop over cell types
    conn_list = set()
    for k, v in mesh.cells.items():
        # Loop over cells
        for i, corner in enumerate(v):
            clabel = labels[k][i]
            # Loop over connection types
            for mt, mv in conn[k][i].items():
                # Loop over connected cells
                for mi in mv:
                    nlabel = labels[mt][mi]
                    if nlabel not in conn_list:
                        # Line connecting cell centers
                        corner_conn = mesh.cells[mt][mi]
                        center = mesh.points[corner].mean(0)
                        center_conn = mesh.points[corner_conn].mean(0)
                        line = center - center_conn

                        # Area of common face
                        face = np.array([
                            mesh.points[c] for c in corner if c in set(corner).intersection(corner_conn)
                        ])
                        if len(face) == 4:
                            face[[2,3]] = face[[3,2]]
                        area = cell_area(face)

                        # Distance from cell centers to common face
                        point = intersection_line_plane(
                            [ center, center_conn ],
                            face,
                        )
                        d1 = distance_point_point(center, point)
                        d2 = distance_point_point(center_conn, point)

                        # Angle between connection line and gravity force
                        rline = _rotate_xaxis(line, rotation_angle)
                        angle = np.dot(rline, [ 0., 0., -1. ]) / np.linalg.norm(rline)
                        f.write(
                            fmt.format(
                                clabel,         # ID1
                                nlabel,         # ID2
                                "",             # NSEQ
                                "",             # NAD1
                                "",             # NAD2
                                _isot(line),    # ISOT
                                d1,             # D1
                                d2,             # D2
                                area,           # AREAX
                                angle,          # BETAX
                            )
                        )
            conn_list.add(clabel)   # Ignore this connection for next cells


def _isot(line):
    """
    Determine anisotropy direction given the direction of the line
    connecting the cell centers.

    Note
    ----
    It always returns 1 if the connection line is not colinear with X, Y
    or Z.
    """
    if np.dot(line, [ 1., 0., 0.]):
        return 1
    elif np.dot(line, [ 0., 1., 0.]):
        return 2
    elif np.dot(line, [ 0., 0., 1.]):
        return 3


def _rotate_xaxis(points, angle):
    """
    Calculate rotated connecting line for calculation of angle with
    gravity.
    """
    theta = np.deg2rad(angle)
    ct, st = np.cos(theta), np.sin(theta)
    Rx = np.array([
        [ 1., 0., 0. ],
        [ 0., ct, -st ],
        [ 0., st, ct ],
    ])
    return np.dot(Rx, points)