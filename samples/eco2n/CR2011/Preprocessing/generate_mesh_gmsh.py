#%%
import numpy

import toughio


# Import grid
mesh = toughio.mesh.read("gmsh/mesh.msh")

# Process grid
mesh.points[:, [1, 2]] = mesh.points[:, [2, 1]]
mesh.extrude_to_3d(
    height = 1.0,
    axis = 1,
)

# Define boundary conditions
materials = numpy.concatenate(mesh.materials)
bcond = (materials == "BOUND").astype(int)
mesh.cell_data["boundary_condition"] = mesh.split(bcond)

# Define initial conditions
centers = numpy.concatenate(mesh.centers)
incon = numpy.full((mesh.n_cells, 4), -1.0e9)
incon[:, 0] = 1.0e5 - 9810.0 * centers[:, 2]
incon[:, 1] = 0.05
incon[:, 2] = 0.0
incon[:, 3] = 10.0 - 0.025 * centers[:, 2]
mesh.cell_data["initial_condition"] = mesh.split(incon)

# Define permeability modifiers
permeability = numpy.full((mesh.n_cells, 3), -1.0)
permeability[materials == "CENAQ"] = [1.0e-13, 1.0e-13, 1.0e-15]
mesh.cell_data["permeability"] = mesh.split(permeability)

# Export MESH and INCON
mesh.to_tough("MESH", incon_eos = "eco2n")

# Pickle for faster later import
mesh.write("mesh.pickle")