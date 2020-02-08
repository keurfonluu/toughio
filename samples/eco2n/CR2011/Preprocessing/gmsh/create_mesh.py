#%%
import pygmsh as pg


# Variables
xmin, xmax = 0., 2000.
zmin, zmax = -500., -2500.
bnd_thick = 10.

# Initialize geometry
geo = pg.built_in.Geometry()

# Aquifer
cenaq = geo.add_polygon(
    X = [
        [ xmin, -1450., 0. ],
        [ xmax, -1450., 0. ],
        [ xmax, -1550., 0. ],
        [ xmin, -1550., 0. ],
    ],
    lcar = 20.,
)

capro_top = geo.add_polygon(
    X = [
        [ xmin, -1300., 0. ],
        [ xmax, -1300., 0. ],
        [ xmax, -1450., 0. ],
        [ xmin, -1450., 0. ],
    ],
    lcar = [ 50., 100., 100., 50. ],
)

capro_bot = geo.add_polygon(
    X = [
        [ xmin, -1550., 0. ],
        [ xmax, -1550., 0. ],
        [ xmax, -1700., 0. ],
        [ xmin, -1700., 0. ],
    ],
    lcar = [ 50., 100., 100., 50. ],
)

uppaq = geo.add_polygon(
    X = [
        [ xmin, zmin, 0. ],
        [ xmax, zmin, 0. ],
        [ xmax, -1300., 0. ],
        [ xmin, -1300., 0. ],
    ],
    lcar = 500.,
)

basaq = geo.add_polygon(
    X = [
        [ xmin, -1700., 0. ],
        [ xmax, -1700., 0. ],
        [ xmax, zmax, 0. ],
        [ xmin, zmax, 0. ],
    ],
    lcar = 500.,
)

# Boundary elements
bound_left = geo.add_polygon(
    X = [
        [ xmin, zmin, 0. ],
        [ xmin - bnd_thick, zmin, 0. ],
        [ xmin - bnd_thick, zmax, 0. ],
        [ xmin, zmax, 0. ],
        [ xmin, -1700., 0. ],
        [ xmin, -1550., 0. ],
        [ xmin, -1450., 0. ],
        [ xmin, -1300., 0. ],
    ],
    lcar = 100.,
)

bound_right = geo.add_polygon(
    X = [
        [ xmax, zmin, 0. ],
        [ xmax + bnd_thick, zmin, 0. ],
        [ xmax + bnd_thick, zmax, 0. ],
        [ xmax, zmax, 0. ],
        [ xmax, -1700., 0. ],
        [ xmax, -1550., 0. ],
        [ xmax, -1450., 0. ],
        [ xmax, -1300., 0. ],
    ],
    lcar = 100.,
)

bound_top = geo.add_polygon(
    X = [
        [ xmin, zmin, 0. ],
        [ xmax, zmin, 0. ],
        [ xmax + bnd_thick, zmin, 0. ],
        [ xmax + bnd_thick, zmin + bnd_thick, 0. ],
        [ xmin, zmin + bnd_thick, 0. ],
    ],
    lcar = 100.,
)

bound_bot = geo.add_polygon(
    X = [
        [ xmin, zmax, 0. ],
        [ xmax, zmax, 0. ],
        [ xmax + bnd_thick, zmax, 0. ],
        [ xmax + bnd_thick, zmax - bnd_thick, 0. ],
        [ xmin, zmax - bnd_thick, 0. ],
    ],
    lcar = 100.,
)

# Define physical groups
geo.add_physical(
    entities = uppaq.surface,
    label = "UPPAQ",
)
geo.add_physical(
    entities = [
        capro_top.surface,
        capro_bot.surface,
    ],
    label = "CAPRO",
)
geo.add_physical(
    entities = cenaq.surface,
    label = "CENAQ",
)
geo.add_physical(
    entities = basaq.surface,
    label = "BASAQ",
)
geo.add_physical(
    entities = [
        bound_left.surface,
        bound_right.surface,
        bound_top.surface,
        bound_bot.surface,
    ],
    label = "BOUND",
)

# Write mesh file
geo.add_raw_code("Coherence;")
pg.generate_mesh(
    geo,
    dim = 2,
    prune_vertices = True,
    remove_faces = True,
    geo_filename = "mesh.geo",
    msh_filename = "mesh.msh",
    mesh_file_type = "msh4",
    extra_gmsh_arguments = [
        # "-algo", "del2d",
        "-smooth", "2",
        "-optimize_netgen",
    ],
)