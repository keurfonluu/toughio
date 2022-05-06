import helpers
import numpy as np
import pytest

import toughio


def allclose(x, y, atol=1.0e-8):
    if isinstance(x, dict):
        for k, v in x.items():
            try:
                assert allclose(v, y[k], atol=atol)

            except KeyError as e:
                print(y[k])
                raise KeyError(e)

    elif isinstance(x, str):
        assert x == y

    elif np.ndim(x) == 0:
        assert np.allclose(x, y, atol=atol)

    else:
        for xx, yy in zip(x, y):
            assert allclose(xx, yy, atol=atol)

    return True


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
            "react_wdata": [helpers.random_string(5) for _ in range(np.random.randint(10) + 1)],
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

    assert allclose(parameters_ref, parameters, atol=1.0e-4)


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
            "elements": [helpers.random_string(5) for _ in range(np.random.randint(10) + 1)],
            "components": [helpers.random_string(20) for _ in range(np.random.randint(10) + 1)],
            "minerals": np.random.randint(10, size=np.random.randint(10) + 1),
            "aqueous_species": [helpers.random_string(20) for _ in range(np.random.randint(10) + 1)],
            "surface_complexes": np.random.randint(10, size=np.random.randint(10) + 1),
            "exchange_species": [helpers.random_string(20) for _ in range(np.random.randint(10) + 1)],
        },
        "default": {
            "initial_water": np.random.randint(10),
            "injection_water": np.random.randint(10),
            "mineral": np.random.randint(10),
            "gas": np.random.randint(10),
            "adsorption": np.random.randint(10),
            "ion_exchange": np.random.randint(10),
            "porosity_permeability": np.random.randint(10),
            "linear_adsorption": np.random.randint(10),
            "injection_gas": np.random.randint(10),
        },
        "zones": {
            helpers.random_string(5): {
                "nseq": np.random.randint(10),
                "nadd": np.random.randint(10),
                "initial_water": np.random.randint(10),
                "injection_water": np.random.randint(10),
                "mineral": np.random.randint(10),
                "gas": np.random.randint(10),
                "adsorption": np.random.randint(10),
                "ion_exchange": np.random.randint(10),
                "porosity_permeability": np.random.randint(10),
                "linear_adsorption": np.random.randint(10),
                "injection_gas": np.random.randint(10),
            }
            for _ in range(np.random.randint(10) + 1)
        },
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

    assert allclose(parameters_ref, parameters, atol=1.0e-3)
