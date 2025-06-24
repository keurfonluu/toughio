#%%
import intera
import matplotlib.pyplot as plt
import numpy as np
import toughio
import pyvista as pv
import time

%load_ext autoreload
%autoreload 2

ignore_elements = {
    "MAL00",
    "EFF00",
    "PAS00",
    "UPB00",
    "LOB00",
    "KEU00",
    "OMU00",
}

output = toughio.read_output("C:/Users/KLuu/Downloads/particle_tracking/mikey/SMA_ZNO_2Dhr_gv1_pv1_gas.out", connection=True, time_steps=-1)
for i, (l1, l2) in enumerate(output.labels):
    output.labels[i] = [l1.replace(" ", "0"), l2.replace(" ", "0")]

starttime = time.time()
output = output.to_element("C:/Users/KLuu/Downloads/particle_tracking/mikey/SMA_ZNO_2Dhr_gv1_pv1_gas", list(output.data), ignore_elements=ignore_elements)
print(time.time() - starttime)

mesh = pv.read("C:/Users/KLuu/Downloads/particle_tracking/mikey/mesh.vtu")
mesh.points[:, [1, 2]] = mesh.points[:, [2, 1]]

pt = toughio.ParticleTracker(mesh, velocity=output.data["V(GAS)"])
particles = mesh.cell_centers().points[mesh["ROCK"] > 2]
pathlines = pt.track(particles)

for pathline in pathlines:
    plt.plot(*pathline[:, [0, 2]].T, c="black", alpha=0.1)
