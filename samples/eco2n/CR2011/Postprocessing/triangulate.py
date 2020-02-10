#%%
import toughio
import numpy
import pyvista


# Import last time step of output file
output = toughio.read_output("../OUTPUT_ELEME.csv")[-1]

# Create point array from 'X' and 'Z' coordinates in output file
# Triangulation will fail if we use 'Y' since the problem is 2D
points = numpy.column_stack((output.data["X"], output.data["Z"]))

# Create triangulated mesh from points
mesh = toughio.meshmaker.triangulate(points)

# Attach data to points in mesh
for label, data in output.data.items():
    mesh.add_point_data(label, data)

# Export to another file format (e.g. VTK, Tecplot...)
mesh.write("OUTPUT.dat", file_format="tecplot")