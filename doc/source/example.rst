Sample problem
==============

This section intends to describe a simple yet complete workflow from setting up a TOUGH simulation with :mod:`toughio` to importing and visualizing simulation results in Python.

The model geometry used is inspired from the paper:

..

    Cappa, Frédéric, and Jonny Rutqvist. "Modeling of Coupled Deformation and Permeability Evolution during Fault Reactivation Induced by Deep Underground Injection of CO2." International Journal of Greenhouse Gas Control 5, no. 2 (March 2011): 336–346. <https://doi.org/10.1016/j.ijggc.2010.08.005>.

The fault modeled in this sample problem has already been reactivated by increasing the permeability from its original value.

Note that only the main :mod:`toughio` features are introduced.


Generate mesh in Python with Gmsh
---------------------------------

This section describes how to generate a mesh using Gmsh in Python. It requires PyGmsh to be installed:

.. code-block::

    pip install pygmsh --user

The mesh can also be generated from scratch directly in Gmsh either using its GUI and/or its internal scripting language.

Note that :mod:`toughio` is not required at this preliminary stage of the pre-processing. This section only intends to show how the mesh used in this sample problem has been generated. The user is free to use any meshing software as long as the mesh format is supported by :mod:`toughio` (through :mod:`meshio`).

First, we import numpy and pygmsh, and initialize a pygmsh.Geometry object that will be used to construct all the geometrical entities of the model.

.. code-block:: python

    import numpy
    import pygmsh

    geo = pygmsh.built_in.Geometry()