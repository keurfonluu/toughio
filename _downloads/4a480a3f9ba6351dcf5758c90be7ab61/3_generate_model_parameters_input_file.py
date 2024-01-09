"""
Generate model parameters input file
====================================

Now that the mesh has been pre-processed, we can define the TOUGH simulation parameters.

"""

########################################################################################
# As always, we first import the required modules for this example.

import numpy as np
import toughio

########################################################################################

########################################################################################
# A :mod:`toughio` input file is defined as a nested dictionary with meaningful keywords.
# Let's initialize our parameter dictionary by giving the simulation a title and defining the equation-of-state. This example will also be run isothermally.

parameters = {
    "title": "Simulation of CO2 leak along a fault",
    "eos": "eco2n",
    "isothermal": True,
    "start": True,
}

########################################################################################

########################################################################################
# We can also define some default values that are shared by the different materials.

parameters["default"] = {
    "density": 2260.0,
    "conductivity": 1.8,
    "specific_heat": 1500.0,
    "compressibility": 8.33e-10,
    "conductivity_dry": 1.8,
    "tortuosity": 0.7,
    "relative_permeability": {
        "id": 3,
        "parameters": [0.3, 0.05],
    },
    "capillarity": {
        "id": 7,
        "parameters": [0.457, 0.0, 5.03e-5, 5.0e7, 0.99],
    },
}

########################################################################################

########################################################################################
# Now, we define specific material properties (different than the default ones previously defined) for each material in the mesh (i.e., we write the block `ROCKS`).

parameters["rocks"] = {
    "UPPAQ": {
        "porosity": 0.10,
        "permeability": 1.0e-14,
    },
    "CENAQ": {
        "porosity": 0.10,
        "permeability": 1.0e-13,
    },
    "BASAQ": {
        "porosity": 0.01,
        "permeability": 1.0e-16,
        "relative_permeability": {
            "id": 3,
            "parameters": [0.3, 0.05],
        },
        "capillarity": {
            "id": 7,
            "parameters": [0.457, 0.0, 1.61e-6, 5.0e7, 0.99],
        },
    },
    "CAPRO": {
        "porosity": 0.01,
        "permeability": 1.0e-19,
        "relative_permeability": {
            "id": 3,
            "parameters": [0.3, 0.05],
        },
        "capillarity": {
            "id": 7,
            "parameters": [0.457, 0.0, 1.61e-6, 5.0e7, 0.99],
        },
    },
    "FAULT": {
        "porosity": 0.10,
        "permeability": 1.0e-13,
    },
    "BOUND": {
        "specific_heat": 1.0e55,
        "porosity": 0.10,
        "permeability": 1.0e-13,
    },
}

########################################################################################

########################################################################################
# We can specify some simulation parameters (block `PARAM`), options (`MOP`) and selections (block `SELEC`).

parameters["options"] = {
    "n_cycle": 9999,
    "n_cycle_print": 9999,
    "t_ini": 0.0,
    "t_max": 3.0 * 365.25 * 24.0 * 3600.0,
    "t_steps": 24.0 * 3600.0,
    "t_step_max": 1.0e8,
    "t_reduce_factor": 4,
    "eps1": 1.0e-4,
    "eps2": 1.0,
    "gravity": 9.81,
}
parameters["extra_options"] = {
    16: 4,
    21: 8,
}
parameters["selections"] = {
    "integers": {
        1: 1,
        13: 2,
        16: 2,
    },
    "floats": [0.8, 0.8],
}

########################################################################################

########################################################################################
# We also have to define the generator (i.e., the source).
# However, we first need to know the name of the cell in which the CO2 is injected. Let's unpickle the mesh back and use the method :meth:`toughio.Mesh.near` to get the name of the injection element.

mesh = toughio.read_mesh("mesh.pickle")
label = mesh.labels[mesh.near((0.0, 0.0, -1500.0))]

########################################################################################

########################################################################################
# Now we can add the generator to the parameters by specifying the type and injection rate (block `GENER`).

parameters["generators"] = [
    {
        "label": label,
        "type": "COM3",
        "rates": 0.02,
    },
]

########################################################################################

########################################################################################
# Let's customize the outputs.
# For this example, we want TOUGH to save the output every three months (i.e., 4 outputs per year). To reduce the size of the output file, we also want TOUGH to only save the saturation of phase 1 (gas) in addition to the cell coordinates. Note that this option is only available in TOUGH3.

parameters["times"] = np.arange(1, 13) * 90.0 * 24.0 * 3600.0
parameters["output"] = {
    "variables": [
        {"name": "saturation", "options": 1},
        {"name": "coordinate"},
    ],
}

########################################################################################

########################################################################################
# Finally, we can export the model parameters input file by using the function :func:`toughio.write_input`.

toughio.write_input("INFILE", parameters)

########################################################################################

########################################################################################
# At this stage, all the input files required to run the simulation have been generated. We can now simply call TOUGH using EOS ECO2n (e.g., :code:`tough3-eco2n` for TOUGH3).

########################################################################################
