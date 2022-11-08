import helpers
import numpy as np
import pytest

import toughio


def test_flow():
    def write_read(x):
        writer_kws = {"file_format": "toughreact-flow"}
        reader_kws = {"file_format": "toughreact-flow"}

        return helpers.write_read(
            "flow.inp",
            x,
            toughio.write_input,
            toughio.read_input,
            writer_kws,
            reader_kws,
        )

    parameters_ref = {
        "rocks": {
            helpers.random_string(5): {
                "tortuosity": -np.random.rand(),
                "porosity_crit": np.random.rand(),
                "tortuosity_exponent": np.random.rand(),
            },
            helpers.random_string(5): {
                "relative_permeability": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
                "capillarity": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
            },
            helpers.random_string(5): {
                "react_tp": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
            },
            helpers.random_string(5): {
                "react_hcplaw": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
            },
            helpers.random_string(5): {
                "react_tp": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
                "react_hcplaw": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
            },
            helpers.random_string(5): {
                "relative_permeability": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
                "react_tp": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
            },
            helpers.random_string(5): {
                "capillarity": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
                "react_hcplaw": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
            },
            helpers.random_string(5): {
                "relative_permeability": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
                "capillarity": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
                "react_tp": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(3),
                },
                "react_hcplaw": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(4),
                },
            },
        },
        "react": {
            "options": {k + 1: v for k, v in enumerate(np.random.randint(10, size=25))},
            "output": {
                "format": np.random.randint(10),
                "shape": np.random.randint(100, size=3),
            },
            "poiseuille": {
                "start": np.random.rand(2),
                "end": np.random.rand(2),
                "aperture": np.random.rand(),
            },
        },
        "options": {
            "react_wdata": [
                helpers.random_string(5) for _ in range(np.random.randint(10) + 1)
            ],
        },
        "initial_conditions": {
            helpers.random_string(5): {
                "values": np.random.rand(4),
                "permeability": np.random.rand(3),
            },
        },
        "generators": [
            {
                "label": helpers.random_string(5),
                "type": helpers.random_string(4),
                "rates": np.random.rand(),
                "specific_enthalpy": np.random.rand(),
            },
            {
                "label": helpers.random_string(5),
                "type": helpers.random_string(4),
                "times": np.random.rand(10),
                "rates": np.random.rand(10),
                "specific_enthalpy": np.random.rand(10),
            },
            {
                "label": helpers.random_string(5),
                "type": helpers.random_string(4),
                "rates": np.random.rand(),
                "specific_enthalpy": np.random.rand(),
                "conductivity_times": np.random.rand(5),
                "conductivity_factors": np.random.rand(5),
            },
            {
                "label": helpers.random_string(5),
                "type": helpers.random_string(4),
                "times": np.random.rand(10),
                "rates": np.random.rand(10),
                "specific_enthalpy": np.random.rand(10),
                "conductivity_times": np.random.rand(9),
                "conductivity_factors": np.random.rand(9),
            },
        ],
    }
    parameters = write_read(parameters_ref)

    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)


@pytest.mark.parametrize(
    "verbose, mopr_10, mopr_11",
    [
        (True, 0, 0),
        (True, 2, 0),
        (True, 0, 1),
        (True, 0, 2),
        (False, 0, 0),
        (False, 2, 0),
        (False, 0, 1),
        (False, 0, 2),
    ],
)
def test_solute(verbose, mopr_10, mopr_11):
    def write_read(x):
        writer_kws = {
            "file_format": "toughreact-solute",
            "verbose": verbose,
            "mopr_10": mopr_10,
            "mopr_11": mopr_11,
        }
        reader_kws = {
            "file_format": "toughreact-solute",
            "mopr_11": mopr_11,
        }

        return helpers.write_read(
            "solute.inp",
            x,
            toughio.write_input,
            toughio.read_input,
            writer_kws,
            reader_kws,
        )

    parameters_ref = {
        "title": helpers.random_string(80),
        "options": {
            "sl_min": np.random.rand(),
            "rcour": np.random.rand(),
            "ionic_strength_max": np.random.rand(),
            "mineral_gas_factor": np.random.rand(),
            "w_time": np.random.rand(),
            "w_upstream": np.random.rand(),
            "aqueous_diffusion_coefficient": np.random.rand(),
            "molecular_diffusion_coefficient": np.random.rand(),
            "n_iteration_tr": np.random.randint(100),
            "eps_tr": np.random.rand(),
            "n_iteration_ch": np.random.randint(100),
            "eps_ch": np.random.rand(),
            "eps_mb": np.random.rand(),
            "eps_dc": np.random.rand(),
            "eps_dr": np.random.rand(),
            "n_cycle_print": np.random.randint(100),
        },
        "flags": {
            "iteration_scheme": np.random.randint(10),
            "reactive_surface_area": np.random.randint(10),
            "solver": np.random.randint(10),
            "n_subiteration": np.random.randint(10),
            "gas_transport": np.random.randint(10),
            "verbosity": np.random.randint(10),
            "feedback": np.random.randint(10),
            "coupling": np.random.randint(10),
            "aqueous_concentration_unit": np.random.randint(10),
            "mineral_unit": np.random.randint(10),
            "gas_concentration_unit": np.random.randint(10),
        },
        "files": {
            "thermodynamic_input": helpers.random_string(20),
            "iteration_output": helpers.random_string(20),
            "plot_output": helpers.random_string(20),
            "solid_output": helpers.random_string(20),
            "gas_output": helpers.random_string(20),
            "time_output": helpers.random_string(20),
        },
        "output": {
            "elements": [
                helpers.random_string(5) for _ in range(np.random.randint(10) + 1)
            ],
            "components": [
                helpers.random_string(20) for _ in range(np.random.randint(10) + 1)
            ],
            "minerals": np.random.randint(10, size=np.random.randint(10) + 1),
            "aqueous_species": [
                helpers.random_string(20) for _ in range(np.random.randint(10) + 1)
            ],
            "surface_complexes": np.random.randint(10, size=np.random.randint(10) + 1),
            "exchange_species": [
                helpers.random_string(20) for _ in range(np.random.randint(10) + 1)
            ],
        },
        "default": {
            "initial_water": np.random.randint(10),
            "injection_water": np.random.randint(10),
            "mineral": np.random.randint(10),
            "initial_gas": np.random.randint(10),
            "adsorption": np.random.randint(10),
            "cation_exchange": np.random.randint(10),
            "permeability_porosity": np.random.randint(10),
            "linear_kd": np.random.randint(10),
            "injection_gas": np.random.randint(10),
        },
        "zones": {
            helpers.random_string(5): {
                "nseq": np.random.randint(10),
                "nadd": np.random.randint(10),
                "initial_water": np.random.randint(10),
                "injection_water": np.random.randint(10),
                "mineral": np.random.randint(10),
                "initial_gas": np.random.randint(10),
                "adsorption": np.random.randint(10),
                "cation_exchange": np.random.randint(10),
                "permeability_porosity": np.random.randint(10),
                "linear_kd": np.random.randint(10),
                "injection_gas": np.random.randint(10),
            }
            for _ in range(np.random.randint(10) + 1)
        },
        "end_comments": [
            helpers.random_string(80) for _ in range(np.random.randint(5) + 2)
        ],
    }

    if mopr_10 == 2:
        parameters_ref["options"].update(
            {
                "n_iteration_1": np.random.randint(100),
                "n_iteration_2": np.random.randint(100),
                "n_iteration_3": np.random.randint(100),
                "n_iteration_4": np.random.randint(100),
                "t_increase_factor_1": np.random.rand(),
                "t_increase_factor_2": np.random.rand(),
                "t_increase_factor_3": np.random.rand(),
                "t_reduce_factor_1": np.random.rand(),
                "t_reduce_factor_2": np.random.rand(),
                "t_reduce_factor_3": np.random.rand(),
            }
        )

    if mopr_11 == 1:
        parameters_ref["default"]["sedimentation_velocity"] = np.random.rand()
        for zone in parameters_ref["zones"].values():
            zone["sedimentation_velocity"] = np.random.rand()

    elif mopr_11 == 2:
        parameters_ref["default"]["element"] = np.random.randint(10)
        for zone in parameters_ref["zones"].values():
            zone["element"] = np.random.randint(10)

    parameters = write_read(parameters_ref)

    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-3)


@pytest.mark.parametrize("verbose", [True, False])
def test_chemical(verbose):
    def write_read(x):
        writer_kws = {
            "verbose": verbose,
            "file_format": "toughreact-chemical",
        }
        reader_kws = {
            "file_format": "toughreact-chemical",
        }

        return helpers.write_read(
            "chemical.inp",
            x,
            toughio.write_input,
            toughio.read_input,
            writer_kws,
            reader_kws,
        )

    # Number of surface primary species
    nsurfs = np.random.randint(5) + 1

    parameters_ref = {
        "title": helpers.random_string(80),
        "primary_species": [
            {
                "name": helpers.random_string(20),
                "transport": np.random.randint(2),
            }
            for _ in range(np.random.randint(5) + 1)
        ],
        "aqueous_kinetics": [
            {
                "species": [
                    {
                        "name": helpers.random_string(20),
                        "stoichiometric_coeff": np.random.rand(),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ],
                "reaction_affinity": {
                    "id": np.random.randint(5),
                    "cf": np.random.rand(),
                    "logK": np.random.rand(),
                },
                "id": np.random.randint(4),
                "n_mechanism": np.random.randint(10),
                "product": [
                    {
                        "specie": helpers.random_string(20),
                        "flag": np.random.randint(3),
                        "power": np.random.rand(),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ],
                "monod": [
                    {
                        "specie": helpers.random_string(20),
                        "flag": np.random.randint(3),
                        "half_saturation": np.random.rand(),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ],
                "inhibition": [
                    {
                        "specie": helpers.random_string(20),
                        "flag": np.random.randint(3),
                        "constant": np.random.rand(),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ],
            }
            for _ in range(2)
        ],
        "aqueous_species": [
            helpers.random_string(20) for _ in range(np.random.randint(5) + 1)
        ],
        "minerals": [
            {
                "name": helpers.random_string(20),
                "type": 0,
                "kinetic_constraint": 0,
                "solid_solution": np.random.randint(3),
                "precipitation_dry": np.random.randint(3),
                "gap": np.random.rand(),
                "temp1": np.random.rand(),
                "temp2": np.random.rand(),
            },
            {
                "name": helpers.random_string(20),
                "type": 1,
                "kinetic_constraint": 1,
                "solid_solution": np.random.randint(3),
                "precipitation_dry": np.random.randint(3),
                "dissolution": {
                    "k25": np.random.rand(),
                    "rate_ph_dependence": 1,
                    "eta": np.random.rand(),
                    "theta": np.random.rand(),
                    "activation_energy": np.random.rand(),
                    "a": np.random.rand(),
                    "b": np.random.rand(),
                    "c": np.random.rand(),
                    "ph1": np.random.rand(),
                    "slope1": np.random.rand(),
                    "ph2": np.random.rand(),
                    "slope2": np.random.rand(),
                },
            },
            {
                "name": helpers.random_string(20),
                "type": 1,
                "kinetic_constraint": 2,
                "solid_solution": np.random.randint(3),
                "precipitation_dry": np.random.randint(3),
                "precipitation": {
                    "k25": np.random.rand(),
                    "rate_ph_dependence": 2,
                    "eta": np.random.rand(),
                    "theta": np.random.rand(),
                    "activation_energy": np.random.rand(),
                    "a": np.random.rand(),
                    "b": np.random.rand(),
                    "c": np.random.rand(),
                    "volume_fraction_ini": np.random.rand(),
                    "id": np.random.randint(2),
                    "extra_mechanisms": [
                        {
                            "ki": np.random.rand(),
                            "activation_energy": np.random.rand(),
                            "species": [
                                {
                                    "name": helpers.random_string(20),
                                    "power": np.random.rand(),
                                }
                                for _ in range(np.random.randint(5) + 1)
                            ],
                        }
                        for _ in range(np.random.randint(5) + 1)
                    ],
                },
                "gap": np.random.rand(),
                "temp1": np.random.rand(),
                "temp2": np.random.rand(),
            },
            {
                "name": helpers.random_string(20),
                "type": 1,
                "kinetic_constraint": 3,
                "solid_solution": np.random.randint(3),
                "precipitation_dry": np.random.randint(3),
                "dissolution": {
                    "k25": np.random.rand(),
                    "rate_ph_dependence": 0,
                    "eta": np.random.rand(),
                    "theta": np.random.rand(),
                    "activation_energy": np.random.rand(),
                    "a": np.random.rand(),
                    "b": np.random.rand(),
                    "c": np.random.rand(),
                },
                "precipitation": {
                    "k25": np.random.rand(),
                    "rate_ph_dependence": 0,
                    "eta": np.random.rand(),
                    "theta": np.random.rand(),
                    "activation_energy": np.random.rand(),
                    "a": np.random.rand(),
                    "b": np.random.rand(),
                    "c": np.random.rand(),
                    "volume_fraction_ini": np.random.rand(),
                    "id": np.random.randint(2),
                },
                "gap": np.random.rand(),
                "temp1": np.random.rand(),
                "temp2": np.random.rand(),
            },
        ],
        "gaseous_species": [
            {
                "name": helpers.random_string(20),
                "fugacity": np.random.randint(2),
            }
            for _ in range(np.random.randint(5) + 1)
        ],
        "surface_complexes": [
            helpers.random_string(20) for _ in range(np.random.randint(5) + 1)
        ],
        "kd_decay": [
            {
                "name": helpers.random_string(20),
                "decay_constant": np.random.rand(),
                "a": np.random.rand(),
                "b": np.random.rand(),
            }
            for _ in range(np.random.randint(5) + 1)
        ],
        "exchanged_species": [
            {
                "name": helpers.random_string(20),
                "reference": bool(np.random.randint(2)),
                "type": np.random.randint(4),
                "site_coeffs": np.random.rand(3),
            }
            for _ in range(np.random.randint(5) + 1)
        ],
        "exchange_sites_id": np.random.randint(3),
        "zones": {
            "minerals": [
                {
                    "species": [
                        {
                            "name": helpers.random_string(20),
                            "volume_fraction_ini": np.random.rand(),
                            "flag": 0,
                        },
                        {
                            "name": helpers.random_string(20),
                            "volume_fraction_ini": np.random.rand(),
                            "flag": 1,
                            "radius": np.random.rand(),
                            "area_ini": np.random.rand(),
                            "area_unit": np.random.randint(5),
                        },
                    ],
                },
                {
                    "rock": helpers.random_string(5),
                    "species": [
                        {
                            "name": helpers.random_string(20),
                            "volume_fraction_ini": np.random.rand(),
                            "flag": 0,
                        }
                        for _ in range(np.random.randint(5) + 1)
                    ],
                },
            ],
            "permeability_porosity": [
                {
                    "id": np.random.randint(7),
                    "a": np.random.rand(),
                    "b": np.random.rand(),
                }
                for _ in range(np.random.randint(5) + 1)
            ],
            "adsorption": [
                {
                    "flag": np.random.randint(2),
                    "species": [
                        {
                            "name": helpers.random_string(20),
                            "area_unit": np.random.randint(3),
                            "area": np.random.rand(),
                        }
                        for _ in range(nsurfs)
                    ],
                }
                for _ in range(np.random.randint(5) + 1)
            ],
            "linear_kd": [
                [
                    {
                        "name": helpers.random_string(20),
                        "solid_density": np.random.rand(),
                        "value": np.random.rand(),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ]
                for _ in range(np.random.randint(5) + 1)
            ],
            "cation_exchange": [
                np.random.rand(5) for _ in range(np.random.randint(5) + 1)
            ],
        },
        "end_comments": [
            helpers.random_string(80) for _ in range(np.random.randint(5) + 2)
        ],
    }

    # Primary species
    for _ in range(nsurfs):
        tmp = {
            "name": helpers.random_string(20),
            "transport": 2,
            "mineral_name": helpers.random_string(20),
            "sorption_density": np.random.rand(),
            "adsorption_id": np.random.randint(5),
        }
        if tmp["adsorption_id"] == 1:
            tmp["capacitance"] = np.random.rand()

        parameters_ref["primary_species"].append(tmp)

    # Aqueous kinetics
    parameters_ref["aqueous_kinetics"][0]["rate"] = np.random.rand()
    parameters_ref["aqueous_kinetics"][1]["rate"] = {
        "k25": np.random.rand(),
        "Ea": np.random.rand(),
    }

    # Initial and injection water zones
    for key in ["initial_waters", "injection_waters"]:
        parameters_ref["zones"][key] = [
            {
                "temperature": np.random.rand(),
                "pressure": np.random.rand(),
                "species": [
                    {
                        "name": helpers.random_string(20),
                        "flag": np.random.randint(5),
                        "guess": np.random.rand(),
                        "ctot": np.random.rand(),
                        "log_fugacity": np.random.rand(),
                        "nameq": helpers.random_string(10),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ],
            },
            {
                "temperature": np.random.rand(),
                "pressure": np.random.rand(),
                "rock": helpers.random_string(5),
                "species": [
                    {
                        "name": helpers.random_string(20),
                        "flag": np.random.randint(5),
                        "guess": np.random.rand(),
                        "ctot": np.random.rand(),
                        "log_fugacity": np.random.rand(),
                        "nameq": helpers.random_string(10),
                    }
                    for _ in range(np.random.randint(5) + 1)
                ],
            },
        ]

    # Initial and injection gas zones
    for key in ["initial_gases", "injection_gases"]:
        pp = "partial_pressure" if key == "initial_gases" else "mole_fraction"
        parameters_ref["zones"][key] = [
            [
                {
                    "name": helpers.random_string(20),
                    pp: np.random.rand(),
                }
                for _ in range(np.random.randint(5) + 1)
            ]
            for _ in range(np.random.randint(5) + 1)
        ]

    parameters = write_read(parameters_ref)

    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-3)
