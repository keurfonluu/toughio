#%%
import numpy

import toughio


# Grid
bnd_thick = 10.

dx = numpy.diff(numpy.logspace(numpy.log10(100.), numpy.log10(1100.), 30))
dx = numpy.append(dx, bnd_thick)                # Right boundary
dx = numpy.concatenate((dx[::-1], dx))

zaq = [ 143., 127., 111., 96., 81., 67., 52., 36., 27. ]
dz = [ bnd_thick ]                              # Top boundary
dz += zaq + 6 * [ 10. ]                         # Upper aquifer
dz += 10 * [ 10. ] + 4 * [ 12.5 ]               # Upper caprock
dz += 5 * [ 20. ]                               # Central aquifer
dz += 4 * [ 12.5 ] + 10 * [ 10. ]               # Basal caprock
dz += 6 * [ 10. ] + zaq[::-1]                   # Basal aquifer
dz += [ bnd_thick ]                             # Bottom boundary
origin = [ -bnd_thick, 0., -2500. - bnd_thick ]

# Create grid
mesh = toughio.meshmaker(
    dx = dx,
    dy = [ 1. ],
    dz = dz[::-1],
    origin = origin,
    material = "BOUND",
)

# Assign groups
mesh.set_material("UPPAQ", xlim = (0., 2000.), zlim = (-500., -1300.))
mesh.set_material("CAPRO", xlim = (0., 2000.), zlim = (-1300., -1450.))
mesh.set_material("CENAQ", xlim = (0., 2000.), zlim = (-1450., -1550.))
mesh.set_material("CAPRO", xlim = (0., 2000.), zlim = (-1550., -1700.))
mesh.set_material("BASAQ", xlim = (0., 2000.), zlim = (-1700., -2500.))

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