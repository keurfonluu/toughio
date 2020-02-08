#%%
import toughio


# Import mesh and get generator's label
mesh = toughio.mesh.read("mesh.pickle")
gidx = mesh.near((1000.0, 0.0, -1500.0))
label = mesh.labels[gidx[0]][gidx[1]]

# Parameters
tParams = {
    "title": "* Permeability anisotropy in reservoir rock: kh = 100*kv",
    "eos": "eco2n",
    "isothermal": True,
    "default": {
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
    },
    "rocks": {
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
            "capillarity": {
                "id": 7,
                "parameters": [0.457, 0.0, 1.61e-6, 5.0e7, 0.99],
            },
        },
        "CAPRO": {
            "porosity": 0.01,
            "permeability": 1.0e-19,
            "capillarity": {
                "id": 7,
                "parameters": [0.457, 0.0, 1.61e-6, 5.0e7, 0.99],
            },
        },
        "BOUND": {
            "specific_heat": 1.0e55,
            "porosity": 0.10,
            "permeability": 1.0e-13,
        },
    },
    "options": {
        "n_cycle": 9999,
        "t_ini": 0.,
        "t_max": 1.0 * 365.25 * 24.0 * 3600.0,
        "t_steps": 24.0 * 3600.,
        "t_step_max": 1.0e8,
        "t_reduce_factor": 4,
        "eps1": 1.0e-4,
        "eps2": 1.0,
    },
    "extra_options": {
        21: 8,
    },
    "more_options": {
        19: 1,
    },
    "selections": {
        1: 1,
        10: 0,
        11: 0,
        12: 0,
        13: 2,
        14: 0,
        15: 0,
        16: 2,
    },
    "extra_selections": [0.8, 0.8],
    "generators": {
        label: {
            "type": "COM3",
            "rates": 0.02,
        },
    },
}

toughio.write_input("INFILE", tParams)