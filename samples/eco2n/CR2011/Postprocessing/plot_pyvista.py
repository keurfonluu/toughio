#%%
import toughio

import pyvista


# Reload mesh
mesh = toughio.mesh.read("../Preprocessing/mesh.pickle")

# Import TOUGH results into mesh
mesh.read_output("../OUTPUT_ELEME.csv")

# Plot
p = pyvista.Plotter(window_size = (1200, 1200), notebook = False)
p.add_mesh(
    mesh.to_pyvista(),
    scalars = "SAT_G",
    stitle = "Gas saturation",
    cmap = "coolwarm",
    n_colors = 20,
    show_edges = False,
    edge_color = (0.5, 0.5, 0.5),
    scalar_bar_args = {
        "height": 0.1,
        "width": 0.5,
        "position_x": 0.75,
        "position_y": 0.01,
        "vertical": False,
        "n_labels": 4,
        "fmt": "%.3f",
        "title_font_size": 20,
        "font_family": "arial",
        "shadow": True,
    },
)
p.show_grid(
    show_xaxis = True,
    show_yaxis = False,
    show_zaxis = True,
    xlabel = "Distance (m)",
    zlabel = "Elevation (m)",
    ticks = "outside",
    font_family = "arial",
    shadow = True,
)
p.view_xz()
p.show()