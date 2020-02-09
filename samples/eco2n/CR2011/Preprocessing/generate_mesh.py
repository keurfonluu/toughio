#%%
import numpy
import toughio


# Grid
bnd_thick = 10.0

dx = numpy.diff(numpy.logspace(numpy.log10(100.0), numpy.log10(1100.0), 30))
dx = numpy.append(dx, bnd_thick)                # Right boundary
dx = numpy.concatenate((dx[::-1], dx))

zaq = [143.0, 127.0, 111.0, 96.0, 81.0, 67.0, 52.0, 36.0, 27.0]
dz = [bnd_thick]                                # Top boundary
dz += zaq + 6 * [10.0]                          # Upper aquifer
dz += 10 * [10.0] + 4 * [12.5]                  # Upper caprock
dz += 5 * [20.0]                                # Central aquifer
dz += 4 * [12.5] + 10 * [10.0]                  # Basal caprock
dz += 6 * [10.0] + zaq[::-1]                    # Basal aquifer
dz += [bnd_thick]                               # Bottom boundary
origin = [-bnd_thick, 0.0, -2500.0 - bnd_thick]

# Create grid
mesh = toughio.meshmaker(
    dx = dx,
    dy = [1.0],
    dz = dz[::-1],
    origin = origin,
    material = "BOUND",
)

# Assign materials
mesh.set_material("UPPAQ", xlim = (0.0, 2000.0), zlim = (-500.0, -1300.0))
mesh.set_material("CAPRO", xlim = (0.0, 2000.0), zlim = (-1300.0, -1450.0))
mesh.set_material("CENAQ", xlim = (0.0, 2000.0), zlim = (-1450.0, -1550.0))
mesh.set_material("CAPRO", xlim = (0.0, 2000.0), zlim = (-1550.0, -1700.0))
mesh.set_material("BASAQ", xlim = (0.0, 2000.0), zlim = (-1700.0, -2500.0))

# Define boundary conditions
materials = numpy.concatenate(mesh.materials)
bcond = (materials == "BOUND").astype(int)
mesh.add_cell_data("boundary_condition", bcond)

# Define initial conditions
centers = numpy.concatenate(mesh.centers)
incon = numpy.full((mesh.n_cells, 4), -1.0e9)
incon[:, 0] = 1.0e5 - 9810.0 * centers[:, 2]
incon[:, 1] = 0.05
incon[:, 2] = 0.0
incon[:, 3] = 10.0 - 0.025 * centers[:, 2]
mesh.add_cell_data("initial_condition", incon)

# Define permeability modifiers
permeability = numpy.full((mesh.n_cells, 3), -1.0)
permeability[materials == "CENAQ"] = [1.0e-13, 1.0e-13, 1.0e-15]
mesh.add_cell_data("permeability", permeability)

# Export MESH and INCON
mesh.to_tough("MESH", incon_eos = "eco2n")

# Pickle for faster later import
mesh.write("mesh.pickle")