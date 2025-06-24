#%%
import numpy as np
import toughio

%reload_ext autoreload
%autoreload 2


# Contant
day = 24.0 * 3600.0

# Fraction of water 2
X2 = 1.0e-8
# X2 = 0.0

# Generate mesh
mesh = toughio.meshmaker.structured_grid(
    dx=30 * [30.0],
    dy=30 * [30.0],
    dz=1 * [100.0],
    origin=[0.0, 0.0, -100.0],
    material="RESER",
)
mesh.set_material("INJ01", [mesh.find_enclosing_cell([75.0, 825.0, 0.0])])
#%%
# mesh.set_cell_labels(np.array([label.replace(" ", "0") for label in mesh.labels]))
# mesh.write_tough("MESH")
mesh.write("mesh.vtk")

# Get labels of generators
generators = [
    [75.0, 825.0, -50.0],
    [75.0, 75.0, -50.0],
    [825.0, 75.0, -50.0],
    [825.0, 825.0, -50.0],
]
labels = mesh.labels[mesh.find_enclosing_cell(generators)]

# Generate input file
parameters = {
    "title": "Sample problem s02: 2-waters, step tracer",
    "eos": "eos1",
    "n_component": 2,
    "isothermal": False,
    "start": True,
    "default": {
        "density": 2650.0,
        "porosity": 0.01,
        "permeability": 6.0e-13,
        "conductivity": 2.1,
        "specific_heat": 1000.0,
        "initial_condition": [100.0e5, 150.0, X2],
        "relative_permeability": {
            "id": 3,
            "parameters": [0.3, 0.05],
        },
        "capillarity": {
            "id": 1,
            "parameters": [0.0, 0.0, 1.0],
        },
    },
    "rocks": {
        "RESER": {},
        "INJ01": {
            "specific_heat": 1.0e20,
            "initial_condition": [100.0e5, 30.0, X2],
        },
    },
    "options": {
        "verbosity": 2,
        "n_cycle": 500,
        "n_cycle_print": 500,
        "t_max": 25.0 * 365.25 * day,  # 25 years
        "t_steps": 1.0e5,
        "eps1": 1.0e-5,
        "derivative_factor": 1.0e-8,
    },
    "solver": {
        "method": 5,
        "z_precond": "Z3",
        "o_precond": "O0",
        "rel_iter_max": 0.8,
        "eps": 1.0e-7,
    },
    "extra_options": {1: 1, 5: 3, 7: 1, 12: 2, 16: 4},
    # "more_options": {8: 1},
    "times": [
        300.0 * day,
        1.0 * 365.25 * day,
        5.0 * 365.25 * day,
        10.0 * 365.25 * day,
        25.0 * 365.25 * day,
    ],
    "generators": [
        {
            "label": labels[0],
            "type": "COM2",
            "name": "das01",
            "rates": 3.75,
            "specific_enthalpy": 5.0e5,
        },
        {
            "label": labels[0],
            "name": "das02",
            "type": "COM1",
            "rates": 1.0e-10,
            "specific_enthalpy": 5.0e5,
        },
        {
            "label": labels[1],
            "name": "das03",
            "type": "MASS",
            "rates": -1.25,
        },
        {
            "label": labels[2],
            "name": "das04",
            "type": "MASS",
            "rates": -1.25,
        },
        {
            "label": labels[3],
            "name": "das05",
            "type": "MASS",
            "rates": -1.25,
        },
    ],
    "element_history": labels,
    "generator_history": labels[1:],
    "output": {"format": "CSV", "variables": [
        {"name": "COORD"},
        {"name": "PRESSURE"},
        {"name": "HEAT FLOW"},
        {"name": "FLOW"},
        {"name": "FLOW", "options": 1},
        {"name": "FLOW", "options": 2},
        # {"name": "VEL"},
        {"name": "VELOCITY", "options": 2},
        # {"name": "GENERATION"},
        # {"name": "FLOWING ENTHALPY"},
        # {"name": "WELLBORE PRESSURE"},
    ]},
}
parameters.update(mesh.to_tough())

# Run simulation
status = toughio.run(
    exec="tough3-eos1",
    input_filename=parameters,
    # other_filenames=["MESH"],
    docker="tough3-docker:1.2.5",
    working_dir="s02",
    # workers=4,
    use_temp=True,
    # petsc_args=["-pc_type", "asm"],
    # silent=True
)
