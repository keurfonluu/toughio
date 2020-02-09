import numpy

from ..mesh._mesh import Cells, Mesh

__all__ = [
    "triangulate",
]


def triangulate(points, material="dfalt"):
    """
    Generate a triangulated mesh from cloud points.

    Parameters
    ----------
    points : array_like (n_points, 3)
        Cooordinates of points.
    material : str, optional, default 'dfalt'
        Default material name.

    Returns
    -------
    toughio.Mesh
        Output triangulated mesh.
    """
    try:
        from scipy.spatial import Delaunay
    except ImportError:
        raise ModuleNotFoundError(
            "Triangulation requires scipy >= 0.9 to be installed."
        )
    
    assert isinstance(points, (list, tuple, numpy.ndarray))
    assert numpy.ndim(points) == 2
    assert numpy.shape(points)[1] in {2, 3}
    assert isinstance(material, str)

    points = numpy.asarray(points)
    connectivity = Delaunay(points).simplices
    cell_type = "triangle" if points.shape[1] == 2 else "tetra"
    cells = [Cells(cell_type, connectivity)]
    mesh = Mesh(points, cells)
    mesh.add_cell_data("material", numpy.ones(mesh.n_cells, dtype=int))
    mesh.field_data[material] = numpy.array([1, 3])

    return mesh