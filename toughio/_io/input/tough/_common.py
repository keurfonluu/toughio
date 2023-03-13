blocks = {
    "TITLE",
    "DIMEN",
    "ROCKS",
    "RPCAP",
    "REACT",
    "FLAC",
    "CHEMP",
    "NCGAS",
    "MULTI",
    "SOLVR",
    "START",
    "PARAM",
    "SELEC",
    "INDOM",
    "MOMOP",
    "TIMES",
    "HYSTE",
    "FOFT",
    "COFT",
    "GOFT",
    "GENER",
    "TIMBC",
    "DIFFU",
    "OUTPT",
    "OUTPU",
    "ELEME",
    "COORD",
    "CONNE",
    "INCON",
    "MESHM",
    "POISE",
    "NOVER",
    "ENDCY",
    "END COMMENTS",
}

_Parameters = {
    "title": "",
    "eos": "",
    "n_component": None,
    "n_phase": None,
    "n_component_incon": None,
    "do_diffusion": None,
    "react": {},
    "flac": {},
    "chemical_properties": {},
    "non_condensible_gas": [],
    "isothermal": False,
    "start": False,
    "nover": False,
    "rocks": {},
    "options": {},
    "extra_options": {},
    "more_options": {},
    "hysteresis_options": {},
    "selections": {},
    "solver": {},
    "generators": [],
    "diffusion": [],
    "times": [],
    "element_history": [],
    "connection_history": [],
    "generator_history": [],
    "output": {},
    "elements": {},
    "coordinates": False,
    "connections": {},
    "initial_conditions": {},
    "boundary_conditions": {},
    "meshmaker": {},
    "default": {},
    "array_dimensions": {},
    "end_comments": "",
}

Parameters = dict(_Parameters)

flac = {
    "creep": False,
    "porosity_model": None,
    "version": None,
}

chemical_properties = {
    "temperature_crit": None,
    "pressure_crit": None,
    "compressibility_crit": None,
    "pitzer_factor": None,
    "dipole_moment": None,
    "boiling_point": None,
    "vapor_pressure_a": None,
    "vapor_pressure_b": None,
    "vapor_pressure_c": None,
    "vapor_pressure_d": None,
    "molecular_weight": None,
    "heat_capacity_a": None,
    "heat_capacity_b": None,
    "heat_capacity_c": None,
    "heat_capacity_d": None,
    "napl_density_ref": None,
    "napl_temperature_ref": None,
    "gas_diffusivity_ref": None,
    "gas_temperature_ref": None,
    "exponent": None,
    "napl_viscosity_a": None,
    "napl_viscosity_b": None,
    "napl_viscosity_c": None,
    "napl_viscosity_d": None,
    "volume_crit": None,
    "solubility_a": None,
    "solubility_b": None,
    "solubility_c": None,
    "solubility_d": None,
    "oc_coeff": None,
    "oc_fraction": None,
    "oc_decay": None,
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
    "react_wdata": None,
}

extra_options = {k + 1: None for k in range(24)}

more_options = {k + 1: None for k in range(50)}

hysteresis_options = {k + 1: None for k in range(3)}

react_options = {k + 1: None for k in range(25)}

solver = {
    "id": 3,
    "z_precond": "Z0",
    "o_precond": "O0",
    "rel_iter_max": 0.1,
    "eps": 1.0e-6,
}

generators = {
    "label": None,
    "name": None,
    "nseq": None,
    "nadd": None,
    "nads": None,
    "type": None,
    "times": None,
    "rates": None,
    "specific_enthalpy": None,
    "layer_thickness": None,
    "n_layer": None,
    "conductivity_times": None,
    "conductivity_factors": None,
}

boundary_conditions = {
    "label": None,
    "variable": None,
    "times": None,
    "values": None,
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
    "permeability": None,
}

meshmaker = {
    "type": None,
    "parameters": [],
    "angle": None,
}

xyz = {
    "type": None,
    "n_increment": None,
    "sizes": None,
}

rz2d = {
    "type": None,
    "radii": [],
    "n_increment": None,
    "size": None,
    "radius": None,
    "radius_ref": None,
    "thicknesses": [],
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
    "tortuosity_exponent": None,
    "porosity_crit": None,
    "initial_condition": [None for _ in range(6)],
    "relative_permeability": {"id": None, "parameters": []},
    "capillarity": {"id": None, "parameters": []},
    "react_tp": {"id": None, "parameters": []},
    "react_hcplaw": {"id": None, "parameters": []},
    "permeability_model": {"id": 1, "parameters": []},
    "equivalent_pore_pressure": {"id": 3, "parameters": []},
    "phase_composition": None,
}

array_dimensions = {
    "n_rocks": None,
    "n_times": None,
    "n_generators": None,
    "n_rates": None,
    "n_increment_x": None,
    "n_increment_y": None,
    "n_increment_z": None,
    "n_increment_rad": None,
    "n_properties": None,
    "n_properties_times": None,
    "n_regions": None,
    "n_regions_parameters": None,
    "n_ltab": None,
    "n_rpcap": None,
    "n_elements_timbc": None,
    "n_timbc": None,
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
    "ewasg": [3, 4, 3, 6],
    "eco2n": [3, 4, 3, 6],
    "eco2n_v2": [3, 4, 3, 6],
    "eco2m": [3, 4, 4, 6],
    "tmvoc": None,
}

header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"
