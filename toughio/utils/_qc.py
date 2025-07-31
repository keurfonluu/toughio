from __future__ import annotations

import os
from typing import Optional

import numpy as np
import pyvista as pv


def plot_eleme_conne(
    parameters: dict | str | os.PathLike,
    plotter: Optional[pv.Plotter] = None,
    *,
    xscale: Optional[float] = None,
    yscale: Optional[float] = None,
    zscale: Optional[float] = None,
    parallel_projection: bool = False,
    show_elements: bool = True,
    show_connections: bool = True,
    cmap: Optional[str] = None,
    point_size: int = 8,
    line_width: int = 4,
    **kwargs
) -> None:
    """
    Plot elements and/or connections in TOUGH MESH file.

    Parameters
    ----------
    parameters : dict | str | PathLike
        Input file name or parameters.
    xscale : float, optional
        Scaling in the X direction.
    yscale : float, optional
        Scaling in the Y direction.
    zscale : float, optional
        Scaling in the Z direction.
    parallel_projection : bool, default False
        If True, enable parallel projection.
    show_elements : bool, default True
        If True, show elements as Gaussian points.
    show_connections : bool, default True
        If True, show connections as lines.
    cmap : str, optional
        Colormap for the elements.
    point_size : int, default 8
        Size of the points representing elements.
    line_width : int, default 4
        Width of the lines representing connections.
    **kwargs : dict, optional
        Additional keyword arguments. See ``pyvista.Plotter`` for more details.

    """
    from .. import read_input

    if not (show_elements or show_connections):
        raise ValueError()

    if not isinstance(parameters, dict):
        parameters = read_input(parameters, blocks=["ELEME", "CONNE"])

    # Elements
    points = {
        k: [x if x is not None else 0.0 for x in v["center"]]
        for k, v in parameters["elements"].items()
    }

    if show_elements:
        materials = [str(v["material"]) for v in parameters["elements"].values()]
        elements = pv.PolyData(list(points.values()))

    # Connections
    connections = {}

    for k, v in parameters["connections"].items():
        l1, l2 = k[:5], k[5:]

        try:
            line = pv.Line(points[l1], points[l2])

        except KeyError:
            continue
        
        connections.setdefault(v["permeability_direction"], []).append(line)

    # Plot
    p = plotter if plotter is not None else pv.Plotter(**kwargs)

    if xscale or yscale or zscale:
        p.set_scale(xscale, yscale, zscale)

    if show_elements:
        p.add_mesh(
            elements,
            scalars=materials,
            cmap=cmap,
            render_points_as_spheres=True,
            point_size=point_size,
        )
    
    if show_connections:
        for k, v in connections.items():
            if k in {0, 1, 2, 3}:
                v = pv.merge(v)
                color = "black"

            elif k in {4, 5, 6}:
                arrows = []

                for line in v:
                    start = line.points[0]
                    direction = line.points[1] - line.points[0]
                    arrow = pv.Arrow(start, direction)
                    arrows.append(arrow)

                v = pv.merge(arrows)
                color = "blue"

            elif k in {-1, -2, -3}:
                v = pv.merge(v)
                color = "red"

            else:
                raise ValueError(f"{k} not supported")

            p.add_mesh(
                v,
                line_width=line_width,
                color=color,
            )

    p.add_axes()

    if parallel_projection:
        p.enable_parallel_projection()

    if plotter is None:
        p.show()
