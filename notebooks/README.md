# Sample problem

This set of notebooks intends to describe a simple yet complete workflow from setting up a TOUGH simulation with `toughio` to importing and visualizing simulation results in Python. The notebooks should be read in the following order:

-   Preprocessing/0. Generate mesh in Python with Gmsh.ipynb
-   Preprocessing/1. Generate MESH and INCON files.ipynb
-   Preprocessing/2. Generate model parameters input file.ipynb
-   Postprocessing/3. Import and visualize simulation outputs in PyVista.ipynb
-   Postprocessing/4. Generate an animation with PyVista.ipynb

The reader is invited to run the shell script `run.sh` after reading and executing the Preprocessing notebooks.

The model geometry used is inspired from the paper:

> Cappa, Frédéric, and Jonny Rutqvist. "Modeling of Coupled Deformation and Permeability Evolution during Fault Reactivation Induced by Deep Underground Injection of CO2." International Journal of Greenhouse Gas Control 5, no. 2 (March 2011): 336–346. <https://doi.org/10.1016/j.ijggc.2010.08.005>.

The fault modeled in this sample problem has already been reactivated by increasing the permeability from its original value.

Note that only the main `toughio` features are introduced in these notebooks.
