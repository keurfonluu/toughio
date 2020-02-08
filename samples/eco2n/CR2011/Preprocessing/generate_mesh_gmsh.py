#%%
import numpy

import toughio


# Import grid
mesh = toughio.mesh.read("gmsh/mesh.msh")

# Process grid
mesh.points[:,[1,2]] = mesh.points[:,[2,1]]
mesh.extrude_to_3d(
    height = 1.,
    axis = 1,
)

# Define boundary conditions
bc = numpy.zeros(mesh.n_cells)
materials = numpy.concatenate(mesh.materials)
idx = numpy.nonzero(materials == "BOUND")[0]
bc[idx] = 1
mesh.cell_data["boundary_condition"] = mesh.split(bc)

# Define initial conditions
incon = numpy.full((mesh.n_cells, 4), -1.0e9)
centers = numpy.concatenate(mesh.centers)
incon[:,0] = 1.0e5 - 9810.0 * centers[:,2]
incon[:,1] = 0.05
incon[:,2] = 0.0
incon[:,3] = 10.0 - 0.025 * centers[:,2]
mesh.cell_data["initial_condition"] = mesh.split(incon)

# Define permeability
permeability = numpy.full((mesh.n_cells, 3), -1.0)
idx = numpy.nonzero(materials == "CENAQ")[0]
permeability[idx] = [1.0e-13, 1.0e-13, 1.0e-15]
mesh.cell_data["permeability"] = mesh.split(permeability)

# Export MESH and INCON
mesh.to_tough(
    "MESH",
    nodal_distance = "orthogonal",
    incon_eos = "eco2n",
)

# Pickle for faster later import
mesh.write("mesh.pickle")