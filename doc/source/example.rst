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

We can define a bunch of useful variables such as the characteristic length or some parameters to characterize the model.

.. code-block:: python

    lc = 100.0                              # Characteristic length of mesh
    xmin, xmax = 0.0, 2000.0                # X axis boundaries
    zmin, zmax = -500.0, -2500.0            # Z axis boundaries

    inj_z = -1500.0                         # Depth of injection
    flt_offset = 50.0                       # Offset of fault
    flt_thick = 10.0                        # Thickness of fault
    tana = numpy.tan(numpy.deg2rad(80.0))   # Tangeant of dipping angle of fault
    dist = 500.0 - 0.5 * flt_thick          # Distance from injection point (0.0, -1500.0) to left wall of fault

    bnd_thick = 10.0                        # Thickness of boundary elements

We start by defining the geometrical entity representing the fault. The fault is represented as a finite-thickness element that intersects all the layers of the model. To ensure conformity of the final mesh, each wall of the fault is represented by a segmented line where the positions of the nodes correspond to the intersections of the hanging (left) and foot (right) walls with the different layers. Note that the foot wall is inverted so that the fault entity forms a closed rectangular loop.

.. code-block:: python

    depths = [zmin, -1300.0, -1450.0, -1550.0, -1700.0, zmax]
    fault_left = [[dist + (z - inj_z) / tana, z, 0.0] for z in depths]

    depths = [zmin, -1300.0 + flt_offset, -1450.0 + flt_offset, -1550.0 + flt_offset, -1700.0 + flt_offset, zmax]
    fault_right = [[dist + (z - inj_z) / tana + flt_thick, z, 0.0] for z in depths]

    fault = geo.add_polygon(
        X=fault_left + fault_right[::-1],
        lcar=0.1 * lc,
    )

Now, we define the aquifer located at the left side of the fault. To refine the mesh in the injection zone, the characteristic length of each layer entity is increased the farther we get from the injection point. Note that layers are defined such that their characteristic lengths are increasing. This is because Gmsh keeps the first node defined in the geometry in case it detects duplicated nodes.

.. code-block:: python

    cenaq_left = geo.add_polygon(
        X=[
            [xmin, -1450.0, 0.0],
            [dist + (-1450.0 - inj_z) / tana, -1450.0, 0.0],
            [dist + (-1550.0 - inj_z) / tana, -1550.0, 0.0],
            [xmin, -1550.0, 0.0],
        ],
        lcar=0.1 * lc,
    )

    capro_top_left = geo.add_polygon(
        X=[
            [xmin, -1300.0, 0.0],
            [dist + (-1300.0 - inj_z) / tana, -1300.0, 0.0],
            [dist + (-1450.0 - inj_z) / tana, -1450.0, 0.0],
            [xmin, -1450.0, 0.0],
        ],
        lcar=0.2 * lc,
    )

    capro_bot_left = geo.add_polygon(
        X=[
            [xmin, -1550.0, 0.0],
            [dist + (-1550.0 - inj_z) / tana, -1550.0, 0.0],
            [dist + (-1700.0 - inj_z) / tana, -1700.0, 0.0],
            [xmin, -1700.0, 0.0],
        ],
        lcar=0.2 * lc,
    )

    uppaq_left = geo.add_polygon(
        X=[
            [xmin, zmin, 0.0],
            [dist + (zmin - inj_z) / tana, zmin, 0.0],
            [dist + (-1300.0 - inj_z) / tana, -1300.0, 0.0],
            [xmin, -1300.0, 0.0],
        ],
        lcar=2.0 * lc,
    )

    basaq_left = geo.add_polygon(
        X=[
            [xmin, -1700.0, 0.0],
            [dist + (-1700.0 - inj_z) / tana, -1700.0, 0.0],
            [dist + (zmax - inj_z) / tana, zmax, 0.0],
            [xmin, zmax, 0.0],
        ],
        lcar=2.0 * lc,
    )

Likewise, we also define the aquifer located at the right side of the fault.

.. code-block:: python

    cenaq_right = geo.add_polygon(
        X=[
            [dist + (-1450.0 - inj_z + flt_offset) / tana + flt_thick, -1450.0 + flt_offset, 0.0],
            [xmax, -1450.0 + flt_offset, 0.0],
            [xmax, -1550.0 + flt_offset, 0.0],
            [dist + (-1550.0 - inj_z + flt_offset) / tana + flt_thick, -1550.0 + flt_offset, 0.0],
        ],
        lcar=0.75 * lc,
    )

    capro_top_right = geo.add_polygon(
        X=[
            [dist + (-1300.0 - inj_z + flt_offset) / tana + flt_thick, -1300.0 + flt_offset, 0.0],
            [xmax, -1300.0 + flt_offset, 0.0],
            [xmax, -1450.0 + flt_offset, 0.0],
            [dist + (-1450.0 - inj_z + flt_offset) / tana + flt_thick, -1450.0 + flt_offset, 0.0],
        ],
        lcar=0.75 * lc,
    )

    capro_bot_right = geo.add_polygon(
        X=[
            [dist + (-1550.0 - inj_z + flt_offset) / tana + flt_thick, -1550.0 + flt_offset, 0.0],
            [xmax, -1550.0 + flt_offset, 0.0],
            [xmax, -1700.0 + flt_offset, 0.0],
            [dist + (-1700.0 - inj_z + flt_offset) / tana + flt_thick, -1700.0 + flt_offset, 0.0],
        ],
        lcar=0.75 * lc,
    )

    uppaq_right = geo.add_polygon(
        X=[
            [dist + (zmin - inj_z) / tana + flt_thick, zmin, 0.0],
            [xmax, zmin, 0.0],
            [xmax, -1300.0 + flt_offset, 0.0],
            [dist + (-1300.0 - inj_z + flt_offset) / tana + flt_thick, -1300.0 + flt_offset, 0.0],
        ],
        lcar=2.0 * lc,
    )

    basaq_right = geo.add_polygon(
        X=[
            [dist + (-1700.0 - inj_z + flt_offset) / tana + flt_thick, -1700.0 + flt_offset, 0.0],
            [xmax, -1700.0 + flt_offset, 0.0],
            [xmax, zmax, 0.0],
            [dist + (zmax-inj_z) / tana + flt_thick, zmax, 0.0],
        ],
        lcar=2.0 * lc,
    )

Then, we define the boundary elements. In this sample problem, a no-flow boundary condition is imposed on the left side of the model (default in TOUGH), and Dirichlet boundary conditions are imposed elsewhere. Thus, physical boundary elements must be defined at the top, right and bottom sides of the model. Similarly to the fault entity, boundary entities are segmented to ensure conformity of the final mesh.

.. code-block:: python

    bound_right = geo.add_polygon(
        X=[
            [xmax, zmin, 0.0],
            [xmax + bnd_thick, zmin, 0.0],
            [xmax + bnd_thick, zmax, 0.0],
            [xmax, zmax, 0.0],
            [xmax, -1700.0 + flt_offset, 0.0],
            [xmax, -1550.0 + flt_offset, 0.0],
            [xmax, -1450.0 + flt_offset, 0.0],
            [xmax, -1300.0 + flt_offset, 0.0],
        ],
        lcar=lc,
    )

    bound_top = geo.add_polygon(
        X=[
            [xmin, zmin, 0.0],
            [dist + (zmin - inj_z) / tana, zmin, 0.0],
            [dist + (zmin - inj_z) / tana + flt_thick, zmin, 0.0],
            [xmax, zmin, 0.0],
            [xmax + bnd_thick, zmin, 0.0],
            [xmax + bnd_thick, zmin + bnd_thick, 0.0],
            [dist + (zmin - inj_z + bnd_thick) / tana + flt_thick, zmin + bnd_thick, 0.0],
            [dist + (zmin - inj_z + bnd_thick) / tana, zmin + bnd_thick, 0.0],
            [xmin, zmin + bnd_thick, 0.0],
        ],
        lcar=lc,
    )

    bound_bot = geo.add_polygon(
        X=[
            [xmin, zmax, 0.0],
            [dist + (zmax - inj_z) / tana, zmax, 0.0],
            [dist + (zmax - inj_z) / tana + flt_thick, zmax, 0.0],
            [xmax, zmax, 0.0],
            [xmax + bnd_thick, zmax, 0.0],
            [xmax + bnd_thick, zmax - bnd_thick, 0.0],
            [dist + (zmax - inj_z - bnd_thick) / tana + flt_thick, zmax - bnd_thick, 0.0],
            [dist + (zmax - inj_z - bnd_thick) / tana, zmax - bnd_thick, 0.0],
            [xmin, zmax - bnd_thick, 0.0],
        ],
        lcar=lc,
    )

Finally, we assign rock types/materials as Gmsh physical properties.

.. code-block:: python

    geo.add_physical(
        entities=[
            uppaq_left.surface,
            uppaq_right.surface,
        ],
        label="UPPAQ",
    )
    geo.add_physical(
        entities=[
            capro_top_left.surface,
            capro_bot_left.surface,
            capro_top_right.surface,
            capro_bot_right.surface,
        ],
        label="CAPRO",
    )
    geo.add_physical(
        entities=[
            cenaq_left.surface,
            cenaq_right.surface,
        ],
        label="CENAQ",
    )
    geo.add_physical(
        entities=[
            basaq_left.surface,
            basaq_right.surface,
        ],
        label="BASAQ",
    )
    geo.add_physical(
        entities=fault.surface,
        label="FAULT",
    )
    geo.add_physical(
        entities=[
            bound_right.surface,
            bound_top.surface,
            bound_bot.surface,
        ],
        label="BOUND",
    )

Finally, we can generate the Gmsh mesh file directly in Python by specifying the path to Gmsh executable (if Gmsh has not been added to the system PATH).

.. code-block:: python

    geo.add_raw_code("Coherence;")
    mesh = pygmsh.generate_mesh(
        geo,
        dim=2,
        prune_vertices=True,
        remove_lower_dim_cells=True,
        gmsh_path="gmsh",                   # Change the path here
        geo_filename="mesh.geo",
        msh_filename="mesh.msh",
        mesh_file_type="msh4",
        extra_gmsh_arguments=[
            # "-algo", "del2d",
            "-smooth", "2",
            "-optimize_netgen",
        ],
        verbose=False,
    )

Alternatively, we can write the geometry file and import it in Gmsh to generate the final mesh.

.. code-block:: python

    with open("mesh.geo", "w") as f:
        f.write(geo.get_code())

The function pygmsh.generate_mesh returns a meshio.Mesh object that can be visualized with pyvista.

.. code-block:: python

    import pyvista
    pyvista.set_plot_theme("document")

    p = pyvista.Plotter(window_size=(800, 800), notebook=True)
    p.add_mesh(
        mesh=pyvista.from_meshio(mesh),
        stitle="Materials",
        show_scalar_bar=True,
        show_edges=True,
    )
    p.view_xy()
    p.show()


Generate MESH and INCON files
-----------------------------

In this section, we assume that the mesh has already been generated by a third-party software (here Gmsh via :mod:`pygmsh`).

First, we import :mod:`numpy` and :mod:`toughio`.

.. code-block:: python

    import numpy
    import toughio

A supported mesh can be read using the function :func:`toughio.read_mesh` that returns a :class:`toughio.Mesh` object.

.. code-block:: python

    mesh = toughio.read_mesh("mesh.msh")

The mesh used in this sample problem is 2D and has been defined in the XY plane, but the points have 3D coordinates (with zeros as 3rd dimension for every cells). To make it 3D in the XZ plane, we swap the 2nd and 3rd dimensions, and then extrude the mesh by 1 meter along the Y axis (2nd dimension).

.. code-block:: python

    mesh.points[:, [1, 2]] = mesh.points[:, [2, 1]]
    mesh.extrude_to_3d(height=1.0, axis=1)

(Optional) Before going any further, it is good practice to first check the quality of the mesh generated. TOUGH does not use any geometrical coordinate system and assumes that the line connecting a cell with its neighbor is orthogonal to their common interface. :mod:`toughio` provides a mesh property that measures the quality of a cell as the average absolute cosine angle between the line connecting a cell with its neighbor and the normal vector of the common interface. The mesh used in this example is of rather good quality. Bad quality cells are located at the boundaries of the model and mostly belong to the material "BOUND". As this material is only used to impose Dirichlet boundary conditions in TOUGH, these bad quality cells will not impact the simulation outputs.

.. code-block:: python

    import pyvista
    pyvista.set_plot_theme("document")

    p = pyvista.Plotter(window_size=(800, 800), notebook=True)
    p.add_mesh(
        mesh=mesh.to_pyvista(),
        scalars=mesh.qualities,
        stitle="Average cell quality",
        clim=(0.0, 1.0),
        cmap="RdBu",
        show_scalar_bar=True,
        show_edges=True,
    )
    p.view_xz()
    p.show()

(Optional) Usually, a simple distribution plot is enough to rapidly assess the quality of a mesh.

.. code-block:: python

    import seaborn

    ax = seaborn.distplot(mesh.qualities[mesh.materials != "BOUND"], kde=False)


We start by defining the boundary conditions. :mod:`toughio` recognizes the cell data key "boundary_condition" and automatically imposes Dirichlet boundary conditions to cells that have any value other than 0 in this cell data array. In this example, we simply set 1 to cells that belong to the group "BOUND" and 0 to others.

.. code-block:: python
    
    materials = mesh.materials
    bcond = (materials == "BOUND").astype(int)
    mesh.add_cell_data("boundary_condition", bcond)

Initial conditions can be defined as a cell data array associated to key "initial_condition" where each column of the array corresponds to a primary variable. Note that :mod:`toughio` will not write any initial condition value that is lower than the threshold flag -1.0e9.

.. code-block:: python

    centers = mesh.centers
    incon = numpy.full((mesh.n_cells, 4), -1.0e9)
    incon[:, 0] = 1.0e5 - 9810.0 * centers[:, 2]
    incon[:, 1] = 0.05
    incon[:, 2] = 0.0
    incon[:, 3] = 10.0 - 0.025 * centers[:, 2]
    mesh.add_cell_data("initial_condition", incon)

:mod:`toughio` also recognizes the cell data keys "porosity" and "permeability" in case we want to initialize porosity and/or permeability fields (e.g. if well logs data are available). Like boundary and initial conditions, we only have to associate new cell data arrays to keys "porosity" and/or "permeability". The way these arrays are generated does not matter, they can be the results of simple interpolations (e.g. with :mod:`scipy`) or more advanced geostatistical interpolations (e.g. with :mod:`pykrige`).

We can now write the MESH and INCON files by calling the method :meth:`toughio.Mesh.write_tough`. Additionally, we can also pickle the final mesh for later use (reading a pickle file is much faster than reading any mesh format).

.. code-block:: python

    mesh.write_tough("MESH", incon=True)
    mesh.write("mesh.pickle")
