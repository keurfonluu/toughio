"""
Generate input files
====================

The TOUGH input file is shown below and specifies a cylindrical heater of 0.3 m radius and 4.5 m height, that provides a constant output of 3 kW into a porous medium with uniform initial conditions of 18°C temperature, 1 bar pressure, and 20% gas saturation. The mesh consists of a one-dimensional radial grid of 120 active elements extending to a radius of 10,000 m (practically infinite for the time scales of interest here), with an additional inactive element of zero volume representing constant boundary conditions. Properly speaking, the problem represents one unit of an infinite linear string of identical heaters; if a single heater were to be modeled, important end effects would occur at the top and bottom, and a two-dimensional RZ grid would have to be used.

Most of the formation parameters are identical to data used in previous modeling studies of high-level nuclear waste emplacement at Yucca Mountain (Pruess et al., 1990). As we do not include fracture effects in the present simulation, heat pipe effects would be very weak at the low rock matrix permeabilities (of order 1 microdarcy) encountered at Yucca Mountain. To get a more interesting behavior, we have arbitrarily increased absolute permeability by something like a factor 10,000, to 20 millidarcy, and for consistency have reduced capillary pressures by a factor (10,000)\ :sup:`1/2` = 100 in comparison to typical Yucca Mountain data.

.. code-block::

    *rhp* 1-D RADIAL HEAT PIPE
    MESHMAKER1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
    RZ2D
    RADII
        1
            0.
    EQUID
        1             .3
    LOGAR
    99           1.E2
    LOGAR
    20           1.E4
    EQUID
        1            0.0
    LAYER----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
        1
        4.5
    
    ROCKS----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
    POMED    1     2550.       .10   20.E-15   20.E-15   20.E-15       2.0     800.0
                                         .25

    MULTI----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
        2    3    2    6
    START----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
    ----*----1 MOP: 123456789*123456789*1234 ---*----5----*----6----*----7----*----8
    PARAM----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
    2 250     25000003000000002 47 1 1                   1.80
               3.15576E8       -1.
          1.E3      9.E3      9.E4      4.E5
         1.E-5     1.E00                                   1.E-7
                    1.E5                0.20                 18.
    RPCAP----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
        7        0.45000    9.6E-4        1.
        7        0.45000    1.0E-3   8.0E-05      5.E8        1.
    TIMES----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
        3
     3.15576E7  1.2559E8 3.15576E8
    GENER----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8
    A1  1HTR 1                         HEAT       3.E3
    
    ENDCY----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8


This example shows how to generate this file from scratch block by block using :mod:`toughio`.

"""

########################################################################################
# First, we import :mod:`numpy` and :mod:`toughio`.

import numpy as np
import toughio

########################################################################################

########################################################################################
# In this example, we start with the blocks MESHM and LAYER, and use the function :func:`toughio.meshmaker.from_meshmaker` to generate the radial grid. We first define a dictionary with the key "meshmaker" and provide the type of mesh (RZ2D) and the parameters. Once the mesh is generated, we use the method :meth:`toughio.Mesh.write_tough` and :meth:`toughio.Mesh.write` to write the files `MESH` and `mesh.pickle`, respectively. Exporting the mesh is useful for postprocessing as it contains information about the mesh.

parameters = {
    "meshmaker": {
        "type": "rz2d",
        "parameters": [
            {"type": "radii", "radii": [0.0]},
            {"type": "equid", "n_increment": 1, "size": 0.3},
            {"type": "logar", "n_increment": 99, "radius": 100.0},
            {"type": "logar", "n_increment": 20, "radius": 10000.0},
            {"type": "equid", "n_increment": 1, "size": 0.0},
            {"type": "layer", "thicknesses": [4.5]},
        ]
    }
}
mesh = toughio.meshmaker.from_meshmaker(parameters, material="POMED")
mesh.write_tough("MESH")
mesh.write("mesh.pickle")

########################################################################################

########################################################################################
# To generate the main input file, let us initialize a new dictionary with a title (optional).

parameters = {
    "title": "*rhp* 1-D RADIAL HEAT PIPE",
}

########################################################################################

########################################################################################
# The block ROCKS contains a single material and can be defined using the key "rocks", which is a dictionary with keys corresponding to the names of the materials.

parameters["rocks"] = {
    "POMED": {
        "density": 2550.0,
        "porosity": 0.1,
        "permeability": 20.0e-15,
        "conductivity": 2.0,
        "specific_heat": 800.0,
        "tortuosity": 0.25,
    },
}

########################################################################################

########################################################################################
# We can initialize the block MULTI by setting the equation-of-state (EOS3) and the isothermal option. The key "eos" defines the number of mass components and phases while the isothermal option determines the number of equations (i.e., the number of equations is equal to the number of mass components for isothermal simulations). Alternatively, the number of mass components and phases can be fixed using the keys "n_component" and "n_phase", respectively.

parameters["eos"] = "eos3"
parameters["isothermal"] = False

########################################################################################

########################################################################################
# The block START allows INCON data to be defined in arbitrary order and not present for all grid blocks. This option can be enable using the key "start".

parameters["start"] = True

########################################################################################

########################################################################################
# The block PARAM is mainly defined by the key "options". However, the MOP values and the default initial conditions for all grid blocks (last record of the block PARAM) are set in the keys "extra_options" and "default", respectively.

parameters["options"] = {
    "verbosity": 2,
    "n_cycle": 250,
    "n_cycle_print": 250,
    "temperature_dependence_gas": 1.8,
    "t_max": 10.0 * 24.0 * 3600.0 * 365.25,
    "t_steps": [1.0e3, 9.0e3, 9.0e4, 4.0e5],
    "eps1": 1.0e-5,
    "eps2": 1.0,
    "derivative_factor": 1.0e-7,
}
parameters["extra_options"] = {
    1: 1,
    5: 3,
    16: 4,
    17: 7,
    19: 1,
    21: 6,
}
parameters["default"] = {
    "initial_condition": [1.0e5, 0.2, 18.0],
}

########################################################################################

########################################################################################
# The block RPCAP controls the default relative permeability and capillarity models for all materials. Therefore, they are also defined in the dictionary key "default".

parameters["default"]["relative_permeability"] = {
    "id": 7,
    "parameters": [0.45, 0.00096, 1.0],
}
parameters["default"]["capillarity"] = {
    "id": 7,
    "parameters": [0.45, 0.001, 8.0e-5, 5.0e8, 1.0],
}

########################################################################################

########################################################################################
# The block TIMES is simply a list of values (in second) defined using the homologous key "times". Here, we request an output after 1, 4 and 10 years.

parameters["times"] = np.array([1.0, 4.0, 10.0]) * 24.0 * 3600.0 * 365.25

########################################################################################

########################################################################################
# The block GENER is defined by the key "generators" which is a list of dictionaries with keys "label", "name" (optional), "type", "times", "rates" and "specific_enthalpy". "label" is the name of the element where the component is injected/produced. Here, we use the method :meth:`toughio.Mesh.near` to get the index of the element the nearest to the query point.

parameters["generators"] = [
    {
        "label": mesh.labels[mesh.near([0.0, 0.0, 0.0])],
        "name": "HTR 1",
        "type": "HEAT",
        "rates": 3.0e3,
    },
]

########################################################################################

########################################################################################
# Once all the parameters are defined, the input file is ready to written using the function :func:`toughio.write_input`.

toughio.write_input("INFILE", parameters)

########################################################################################
