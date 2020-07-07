"""
Import and visualize simulation outputs in PyVista
==================================================

Once the TOUGH simulation has ended, there is not much things left to do with :mod:`toughio`. We can either:

-   Export the output file *OUTPUT_ELEME.csv* to a file that can be opened by common visualization softwares (e.g. ParaView) using the command line script `toughio-export`,

-   Import the output file *OUTPUT_ELEME.csv* in Python using :mod:`toughio` (two-liners) and do whatever post-processing we want and need.

This example briefly shows how to import TOUGH output file using :mod:`toughio` and how to visualize it with :mod:`pyvista` (adapted from :mod:`pyvista`'s `documentation <https://docs.pyvista.org/>`__).

"""

########################################################################################
# First, we unpickle the mesh file and import the last time step of the output file (`OUTPUT_ELEME.csv` in TOUGH3). For TOUGH2 output, we need to run the command line script `toughio-extract` to convert TOUGH2 main output file to a TOUGH3 output file:
# 
# .. code-block:: bash
#     
#       toughio-extract OUTPUT MESH
# 

import toughio

mesh = toughio.read_mesh("mesh.pickle")
mesh.read_output("OUTPUT_ELEME.csv", time_step=-1)

########################################################################################

########################################################################################
# Once output data have been imported, we can simply call the method :meth:`toughio.Mesh.to_pyvista` to convert the mesh to a :class:`pyvista.UnstructuredGrid` object that can be processed by :mod:`pyvista`.

import pyvista
pyvista.set_plot_theme("document")

p = pyvista.Plotter(window_size=(1000, 1000), notebook=True)
p.add_mesh(
    mesh.to_pyvista(),
    scalars="SAT_G",
    stitle="Gas saturation",
    cmap="viridis_r",
    clim=(0.0, 1.0),
    n_colors=20,
    show_edges=False,
    edge_color=(0.5, 0.5, 0.5),
    scalar_bar_args={
        "height": 0.1,
        "width": 0.5,
        "position_x": 0.75,
        "position_y": 0.01,
        "vertical": False,
        "n_labels": 6,
        "fmt": "%.1f",
        "title_font_size": 20,
        "font_family": "arial",
        "shadow": True,
    },
)
p.show_grid(
    show_xaxis=True,
    show_yaxis=False,
    show_zaxis=True,
    xlabel="Distance (m)",
    zlabel="Elevation (m)",
    ticks="outside",
    font_family="arial",
    shadow=True,
)
p.view_xz()
p.show()

########################################################################################
