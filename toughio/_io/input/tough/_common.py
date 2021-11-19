_Parameters = {
    "title": "",
    "eos": "",
    "n_component": None,
    "n_phase": None,
    "n_component_incon": None,
    "flac": None,
    "non_condensible_gas": None,
    "isothermal": False,
    "start": True,
    "nover": False,
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
    "elements": {},
    "elements_order": None,
    "coordinates": False,
    "connections": {},
    "connections_order": None,
    "initial_conditions": {},
    "initial_conditions_order": None,
    "default": {},
}

Parameters = dict(_Parameters)

flac = {
    "creep": False,
    "porosity_model": None,
    "version": None,
}

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
    "gravity": None,
    "mesh_scale_factor": None,
    "eps1": None,
    "eps2": None,
    "w_upstream": None,
    "w_newton": None,
    "derivative_factor": None,
}

extra_options = {k + 1: None for k in range(24)}

more_options = {k + 1: None for k in range(40)}

solver = {
    "id": 3,
    "z_precond": "Z0",
    "o_precond": "O0",
    "rel_iter_max": 0.1,
    "eps": 1.0e-6,
}

generators = {
    "name": None,
    "nseq": None,
    "nadd": None,
    "nads": None,
    "type": None,
    "times": None,
    "rates": None,
    "specific_enthalpy": None,
    "layer_thickness": None,
}

output = {
    "format": None,
    "variables": None,
}

elements = {
    "nseq": None,
    "nadd": None,
    "material": "",
    "volume": None,
    "heat_exchange_area": None,
    "permeability_modifier": None,
    "center": None,
}

connections = {
    "nseq": None,
    "nadd": None,
    "permeability_direction": None,
    "nodal_distances": None,
    "interface_area": None,
    "gravity_cosine_angle": None,
    "radiant_emittance_factor": None,
}

initial_conditions = {
    "porosity": None,
    "userx": [None for _ in range(5)],
    "values": [None for _ in range(4)],
}

default = {
    "density": None,
    "porosity": None,
    "permeability": None,
    "conductivity": None,
    "specific_heat": None,
    "compressibility": None,
    "expansivity": None,
    "conductivity_dry": None,
    "tortuosity": None,
    "klinkenberg_parameter": None,
    "distribution_coefficient_3": None,
    "distribution_coefficient_4": None,
    "initial_condition": [None for _ in range(6)],
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
    "tmvoc": None,
}

header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"
