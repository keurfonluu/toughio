# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

from __future__ import division

import numpy as np

__all__ = [
    "intersection_line_plane",
    "distance_point_point",
    "distance_point_plane",
    "cell_area",
    "cell_volume",
]


def intersection_line_plane(line, plane):
    """
    Calculate intersection point between a line defined by two points and a
    plane defined by three points.

    Parameters
    ----------
    line : array_like
        Line connecting two points. Each row corresponds to one point.
    plane : array_like
        Plane defined by three points. Each row corresponds to one point.

    Returns
    -------
    ndarray
        Intersection between input line and plane.
    
    Note
    ----
    Cases for ``np.dot(d_vec, n_vec) == 0`` are ignored for optimization
    purpose (it should never happen anyway).
    """
    l0, l1 = np.asarray(line)
    p0, p1, p2 = np.asarray(plane[:3])
    d_vec, n_vec = l1 - l0, np.cross(p0-p2, p1-p2)
    return l0 + np.dot(p0-l0, n_vec) / np.dot(d_vec, n_vec) * d_vec


def distance_point_point(point1, point2):
    """
    Calculate distance between two points.

    Parameters
    ----------
    point1 : array_like
        First point coordinates.
    point2 : array_like
        Second point coordinates.

    Returns
    -------
    float
        Euclidean distance between first and second points.
    """
    return np.linalg.norm(np.asarray(point1)-np.asarray(point2))


def distance_point_plane(point, plane):
    """
    Calculate orthogonal distance of a point to a plane.

    Parameters
    ----------
    point1 : array_like
        Point coordinates.
    plane : array_like
        Plane defined by three points. Each row corresponds to one point.
    
    Returns
    -------
    float
        Orthogonal distance between input point and plane.
    """
    p0, p1, p2 = np.asarray(plane[:3])
    n_vec = np.cross(p0-p2, p1-p2)
    n_vec /= np.linalg.norm(n_vec)
    return np.abs(np.dot(point-p2, n_vec))


def cell_area(points, meshio_type = None):
    """
    Calculate cell area for quad and triangle.

    Parameters
    ----------
    points : array_like
        Cell defined by n points. Each row corresponds to one point.
    meshio_type : str ('triangle' or 'quad'), optional, default None
        Cell type. If `None`, it will be guessed from the number of points.
    
    Returns
    -------
    float
        Cell area.
    """
    if not meshio_type:
        func = {
            3: _area_triangle,
            4: _area_quad,
        }
        return func[len(points)](points)
    else:
        func = {
            "triangle": _area_triangle,
            "quad": _area_quad,
        }
        return func[meshio_type](points)


def _area_triangle(points):
    """
    Calculate area of a triangle.
    """
    p0, p1, p2 = np.asarray(points)
    n_vec = np.cross(p0-p2, p1-p2)
    return 0.5 * np.linalg.norm(n_vec)


def _area_quad(points):
    """
    Calculate area of a quad as the sum of 2 triangles.
    """
    tri = [
        [ 0, 1, 2 ],
        [ 0, 2, 3 ],
    ]
    return np.sum([ _area_triangle(np.asarray(points)[t]) for t in tri ])


def cell_volume(points, meshio_type = None):
    """
    Calculate cell volume for tetrahedron, pyramid, wedge and hexahedron.
    
    Parameters
    ----------
    points : array_like
        Cell defined by n points. Each row corresponds to one point.
    meshio_type : str ('tetra', 'pyramid', 'wedge' or 'hexahedron'),
        optional, default None
        Cell type. If `None`, it will be guessed from the number of points.
    
    Returns
    -------
    float
        Cell volume.
    """
    if not meshio_type:
        func = {
            4: _volume_tetra,
            5: _volume_pyramid,
            6: _volume_wedge,
            8: _volume_hexahedron,
        }
        return func[len(points)](points)
    else:
        func = {
            "tetra": _volume_tetra,
            "pyramid": _volume_pyramid,
            "wedge": _volume_wedge,
            "hexahedron": _volume_hexahedron,
        }
        return func[meshio_type](points)


def _volume_tetra(points):
    """
    Calculate volume of a tetrahedron.
    """
    p0, p1, p2, p3 = np.asarray(points)
    return np.abs(np.dot(p0-p3, np.cross(p1-p3, p2-p3))) / 6.


def _volume_pyramid(points):
    """
    Calculate volume of a pyramid as the sum of 2 tetrahedra.
    """
    tetra = [
        [ 0, 1, 3, 4 ],
        [ 1, 2, 3, 4 ],
    ]
    return np.sum([ _volume_tetra(np.asarray(points)[t]) for t in tetra ])


def _volume_wedge(points):
    """
    Calculate volume of a wedge as the sum of 3 tetrahedra.
    """
    tetra = [
        [ 0, 1, 2, 5 ],
        [ 0, 1, 4, 5 ],
        [ 0, 3, 4, 5 ],
    ]
    return np.sum([ _volume_tetra(np.asarray(points)[t]) for t in tetra ])


def _volume_hexahedron(points):
    """
    Calculate volume of a hexahedron as the sum of 5 tetrahedra.
    """
    tetra = [
        [ 0, 1, 3, 4 ],
        [ 1, 4, 5, 6 ],
        [ 1, 2, 3, 6 ],
        [ 3, 4, 6, 7 ],
        [ 1, 3, 4, 6 ],
    ]
    return np.sum([ _volume_tetra(np.asarray(points)[t]) for t in tetra ])