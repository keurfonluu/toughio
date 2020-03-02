__all__ = [
    "Parameters",
    "selections",
    "options",
    "extra_options",
    "more_options",
    "solver",
    "generators",
    "output",
    "default",
    "eos",
    "header",
]


_Parameters = {
    "title": "",
    "eos": "",
    "n_component": None,
    "n_phase": None,
    "n_component_mass": None,
    "flac": False,
    "creep": False,
    "porosity_model": 0,
    "isothermal": False,
    "start": True,
    "nover": False,
    "endfi": False,
    "rocks": {},
    "rocks_order": None,
    "options": {},
    "extra_options": {},
    "more_options": {},
    "selections": {},
    "solver": {},
    "generators": {},
    "diffusion": None,
    "times": None,
    "element_history": None,
    "connection_history": None,
    "generator_history": None,
    "output": None,
    "default": {},
}

Parameters = dict(_Parameters)

selections = {
    "integers": {k + 1: None for k in range(16)},
    "floats": None,
}

options = {
    "n_iteration": None,
    "n_cycle": None,
    "n_second": None,
    "n_cycle_print": None,
    "verbosity": None,
    "temperature_dependence_gas": None,
    "effective_strength_vapor": None,
    "t_ini": None,
    "t_max": None,
    "t_steps": None,
    "t_step_max": None,
    "t_reduce_factor": None,
    "gravity": 9.81,
    "mesh_scale_factor": None,
    "eps1": None,
    "eps2": None,
    "w_upstream": None,
    "w_newton": None,
    "derivative_factor": None,
}

extra_options = {
    k + 1: v
    for k, v in enumerate(
        [
            None,
            0,
            0,
            0,
            None,
            0,
            0,
            None,
            0,
            0,
            0,
            0,
            0,
            None,
            None,
            4,
            None,
            None,
            None,
            None,
            3,
            None,
            None,
            None,
        ]
    )
}

more_options = {k + 1: None for k in range(40)}
more_options[2] = 5

solver = {
    "id": 3,
    "z_precond": "Z0",
    "o_precond": "O0",
    "rel_iter_max": 0.1,
    "eps": 1.0e-6,
}

generators = {
    "type": None,
    "times": None,
    "rates": None,
    "specific_enthalpy": None,
    "layer_thickness": None,
}

output = {
    "format": "csv",
    "variables": None,
}

default = {
    "density": None,
    "porosity": None,
    "permeability": None,
    "conductivity": None,
    "specific_heat": None,
    "compressibility": None,
    "expansion": None,
    "conductivity_dry": None,
    "tortuosity": None,
    "klinkenberg_parameter": None,
    "distribution_coefficient_3": None,
    "distribution_coefficient_4": None,
    "initial_condition": [None for _ in range(4)],
    "relative_permeability": {"id": None, "parameters": []},
    "capillarity": {"id": None, "parameters": []},
    "permeability_model": {"id": 1, "parameters": []},
    "equivalent_pore_pressure": {"id": 3, "parameters": []},
}

eos = {
    "eos1": [1, 2, 2, 6],
    "eos2": [2, 3, 2, 6],
    "eos3": [2, 3, 2, 6],
    "eos4": [2, 3, 2, 6],
    "eos5": [2, 3, 2, 6],
    "eos7": [3, 3, 2, 6],
    "eos8": [3, 3, 3, 6],
    "eos9": [1, 1, 1, 6],
    "eoswasg": [3, 4, 3, 6],
    "eco2n": [3, 4, 3, 6],
    "eco2n_v2": [3, 4, 3, 6],
    "eco2m": [3, 4, 4, 6],
}

header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"
