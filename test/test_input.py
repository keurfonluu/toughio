import helpers
import numpy as np
import pytest

import toughio

write_read = lambda x, **kwargs: helpers.write_read(
    "INFILE", x, toughio.write_input, toughio.read_input, **kwargs
)

write_read_tough = lambda x: write_read(
    x,
    writer_kws={"file_format": "tough"},
    reader_kws={"file_format": "tough"},
)

write_read_json = lambda x: write_read(
    x,
    writer_kws={"file_format": "json"},
    reader_kws={"file_format": "json"},
)

write_read_toughreact = lambda x: write_read(
    x,
    writer_kws={"file_format": "tough", "simulator": "toughreact"},
    reader_kws={"file_format": "tough", "simulator": "toughreact"},
)


@pytest.mark.parametrize(
    "write_read, single",
    [
        (write_read_tough, True),
        (write_read_tough, False),
        (write_read_json, True),
        (write_read_json, False),
    ],
)
def test_title(write_read, single):
    parameters_ref = {
        "title": (
            helpers.random_string(80)
            if single
            else [helpers.random_string(80) for _ in range(np.random.randint(5) + 2)]
        ),
    }
    parameters = write_read(parameters_ref)

    assert parameters_ref["title"] == parameters["title"]


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_rocks(write_read):
    keys = [
        "density",
        "porosity",
        "permeability",
        "conductivity",
        "specific_heat",
        "compressibility",
        "expansivity",
        "conductivity_dry",
        "tortuosity",
        "klinkenberg_parameter",
        "distribution_coefficient_3",
        "distribution_coefficient_4",
    ]
    parameters_ref = {
        "rocks": {
            helpers.random_string(5): {key: np.random.rand() for key in keys[:5]},
            helpers.random_string(5): {
                key: np.random.rand() if key != "permeability" else np.random.rand(3)
                for key in keys[:5]
            },
            helpers.random_string(5): {key: np.random.rand() for key in keys},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
        }
    }
    names = list(parameters_ref["rocks"].keys())
    parameters_ref["rocks"][names[-1]].update(
        {
            "relative_permeability": {
                "id": np.random.randint(10),
                "parameters": np.random.rand(np.random.randint(7) + 1),
            },
        }
    )
    parameters_ref["rocks"][names[-2]].update(
        {
            "capillarity": {
                "id": np.random.randint(10),
                "parameters": np.random.rand(np.random.randint(7) + 1),
            },
        }
    )
    parameters_ref["rocks"][names[-3]].update(
        {
            "relative_permeability": {
                "id": np.random.randint(10),
                "parameters": np.random.rand(np.random.randint(7) + 1),
            },
            "capillarity": {
                "id": np.random.randint(10),
                "parameters": np.random.rand(np.random.randint(7) + 1),
            },
        }
    )
    parameters = write_read(parameters_ref)

    assert sorted(parameters_ref["rocks"].keys()) == sorted(parameters["rocks"].keys())

    for k, v in parameters_ref["rocks"].items():
        for kk, vv in v.items():
            if not isinstance(vv, dict):
                assert np.allclose(vv, parameters["rocks"][k][kk], atol=1.0e-4)
            else:
                helpers.allclose_dict(vv, parameters["rocks"][k][kk], atol=1.0e-4)


@pytest.mark.parametrize(
    "write_read, rpcap",
    [
        (write_read_tough, "rp"),
        (write_read_tough, "cap"),
        (write_read_tough, "both"),
        (write_read_json, "rp"),
        (write_read_json, "cap"),
        (write_read_json, "both"),
    ],
)
def test_rpcap(write_read, rpcap):
    parameters_ref = {"default": {}}
    if rpcap in {"rp", "both"}:
        parameters_ref["default"]["relative_permeability"] = {
            "id": np.random.randint(10),
            "parameters": np.random.rand(np.random.randint(7) + 1),
        }
    if rpcap in {"cap", "both"}:
        parameters_ref["default"]["capillarity"] = {
            "id": np.random.randint(10),
            "parameters": np.random.rand(np.random.randint(7) + 1),
        }
    parameters = write_read(parameters_ref)

    for k, v in parameters_ref["default"].items():
        helpers.allclose_dict(v, parameters["default"][k], atol=1.0e-4)


@pytest.mark.parametrize("write_read", [write_read_toughreact, write_read_json])
def test_react(write_read):
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
            k + 1: v for k, v in enumerate(np.random.randint(10, size=20))
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
                "rates": np.random.rand(),
                "specific_enthalpy": np.random.rand(),
            },
            {
                "label": helpers.random_string(5),
                "times": np.random.rand(10),
                "rates": np.random.rand(10),
                "specific_enthalpy": np.random.rand(10),
            },
            {
                "label": helpers.random_string(5),
                "rates": np.random.rand(),
                "specific_enthalpy": np.random.rand(),
                "conductivity_times": np.random.rand(5),
                "conductivity_factors": np.random.rand(5),
            },
            {
                "label": helpers.random_string(5),
                "times": np.random.rand(10),
                "rates": np.random.rand(10),
                "specific_enthalpy": np.random.rand(10),
                "conductivity_times": np.random.rand(9),
                "conductivity_factors": np.random.rand(9),
            },
        ],
    }
    parameters = write_read(parameters_ref)

    # Block ROCKS
    assert sorted(parameters_ref["rocks"].keys()) == sorted(parameters["rocks"].keys())

    for k, v in parameters_ref["rocks"].items():
        for kk, vv in v.items():
            if not isinstance(vv, dict):
                assert np.allclose(vv, parameters["rocks"][k][kk], atol=1.0e-4)
            else:
                helpers.allclose_dict(vv, parameters["rocks"][k][kk], atol=1.0e-4)

    # Block REACT
    helpers.allclose_dict(parameters_ref["react"], parameters["react"])
    assert parameters_ref["options"]["react_wdata"] == parameters["options"]["react_wdata"]

    # Block INCON
    assert sorted(parameters_ref["initial_conditions"].keys()) == sorted(
        parameters["initial_conditions"].keys()
    )

    for k, v in parameters_ref["initial_conditions"].items():
        for kk, vv in v.items():
            assert np.allclose(vv, parameters["initial_conditions"][k][kk], atol=1.0e-3)

    # Block GENER
    assert len(parameters_ref["generators"]) == len(parameters["generators"])

    for generator_ref, generator in zip(
        parameters_ref["generators"], parameters["generators"]
    ):
        for k, v in generator_ref.items():
            if k == "label":
                assert v == generator[k]

            else:
                assert np.allclose(v, generator[k], atol=1.0e-4)


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_flac(write_read):
    parameters_ref = {
        "flac": {
            "creep": bool(np.random.randint(2)),
            "porosity_model": np.random.randint(10),
            "version": np.random.randint(10),
        },
        "rocks": {
            helpers.random_string(5): {
                "permeability_model": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(np.random.randint(7) + 1),
                },
                "equivalent_pore_pressure": {
                    "id": np.random.randint(10),
                    "parameters": np.random.rand(np.random.randint(7) + 1),
                },
            }
            for _ in np.random.rand(10) + 1
        },
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(parameters_ref["flac"], parameters["flac"])
    for k, v in parameters_ref["rocks"].items():
        for kk, vv in v.items():
            helpers.allclose_dict(vv, parameters["rocks"][k][kk], atol=1.0e-4)


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_chemp(write_read):
    parameters_ref = {
        "chemical_properties": {
            helpers.random_string(20): {
                "temperature_crit": np.random.rand(),
                "pressure_crit": np.random.rand(),
                "compressibility_crit": np.random.rand(),
                "pitzer_factor": np.random.rand(),
                "dipole_moment": np.random.rand(),
                "boiling_point": np.random.rand(),
                "vapor_pressure_a": np.random.rand(),
                "vapor_pressure_b": np.random.rand(),
                "vapor_pressure_c": np.random.rand(),
                "vapor_pressure_d": np.random.rand(),
                "molecular_weight": np.random.rand(),
                "heat_capacity_a": np.random.rand(),
                "heat_capacity_b": np.random.rand(),
                "heat_capacity_c": np.random.rand(),
                "heat_capacity_d": np.random.rand(),
                "napl_density_ref": np.random.rand(),
                "napl_temperature_ref": np.random.rand(),
                "gas_diffusivity_ref": np.random.rand(),
                "gas_temperature_ref": np.random.rand(),
                "exponent": np.random.rand(),
                "napl_viscosity_a": np.random.rand(),
                "napl_viscosity_b": np.random.rand(),
                "napl_viscosity_c": np.random.rand(),
                "napl_viscosity_d": np.random.rand(),
                "volume_crit": np.random.rand(),
                "solubility_a": np.random.rand(),
                "solubility_b": np.random.rand(),
                "solubility_c": np.random.rand(),
                "solubility_d": np.random.rand(),
                "oc_coeff": np.random.rand(),
                "oc_fraction": np.random.rand(),
                "oc_decay": np.random.rand(),
            }
            for _ in np.random.rand(10) + 1
        }
    }
    parameters = write_read(parameters_ref)

    assert len(parameters["chemical_properties"]) == len(
        parameters_ref["chemical_properties"]
    )
    for k, v in parameters_ref["chemical_properties"].items():
        for kk, vv in v.items():
            assert np.allclose(
                vv, parameters["chemical_properties"][k][kk], atol=1.0e-4
            )


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_ncgas(write_read):
    parameters_ref = {
        "non_condensible_gas": [
            helpers.random_string(10) for _ in np.random.rand(10) + 1
        ]
    }
    parameters = write_read(parameters_ref)

    assert len(parameters["non_condensible_gas"]) == len(
        parameters_ref["non_condensible_gas"]
    )
    for v1, v2 in zip(
        parameters["non_condensible_gas"], parameters_ref["non_condensible_gas"]
    ):
        assert v1 == v2


@pytest.mark.parametrize(
    "write_read, isothermal",
    [(write_read_tough, True), (write_read_tough, False)],
)
def test_multi(write_read, isothermal):
    import random

    from toughio._io.input.tough._common import eos

    parameters_ref = {
        "eos": random.choice(
            [k for k in eos.keys() if k not in {"eos7", "eos8", "eos9", "tmvoc"}]
        ),
        "isothermal": isothermal,
    }
    parameters = write_read(parameters_ref)

    multi = [
        parameters["n_component"],
        parameters["n_component"] + 1,
        parameters["n_phase"],
        6,
    ]
    multi_ref = eos[parameters_ref["eos"]]
    assert multi_ref == multi
    assert parameters_ref["isothermal"] == parameters["isothermal"]


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_solvr(write_read):
    parameters_ref = {
        "solver": {
            "method": np.random.randint(10),
            "z_precond": helpers.random_string(2),
            "o_precond": helpers.random_string(2),
            "rel_iter_max": np.random.rand(),
            "eps": np.random.rand(),
        },
    }
    parameters = write_read(parameters_ref)

    assert parameters_ref["solver"]["method"] == parameters["solver"]["method"]
    assert parameters_ref["solver"]["z_precond"] == parameters["solver"]["z_precond"]
    assert parameters_ref["solver"]["o_precond"] == parameters["solver"]["o_precond"]
    assert np.allclose(
        parameters_ref["solver"]["rel_iter_max"],
        parameters["solver"]["rel_iter_max"],
        atol=1.0e-5,
    )
    assert np.allclose(
        parameters_ref["solver"]["eps"], parameters["solver"]["eps"], atol=1.0e-5
    )


@pytest.mark.parametrize(
    "write_read, t_steps, num_pvars",
    [
        (write_read_tough, np.random.rand(), 4),
        (write_read_tough, np.random.rand(np.random.randint(100) + 1), 4),
        (write_read_tough, np.random.rand(np.random.randint(100) + 1), 6),
        (write_read_json, np.random.rand(), 4),
        (write_read_json, np.random.rand(np.random.randint(100) + 1), 4),
        (write_read_json, np.random.rand(np.random.randint(100) + 1), 6),
    ],
)
def test_param(write_read, t_steps, num_pvars):
    parameters_ref = {
        "options": {
            "n_iteration": np.random.randint(10),
            "n_cycle": np.random.randint(10),
            "n_second": np.random.randint(10),
            "n_cycle_print": np.random.randint(10),
            "verbosity": np.random.randint(10),
            "temperature_dependence_gas": np.random.rand(),
            "effective_strength_vapor": np.random.rand(),
            "t_ini": np.random.rand(),
            "t_max": np.random.rand(),
            "t_steps": t_steps,
            "t_step_max": np.random.rand(),
            "t_reduce_factor": np.random.rand(),
            "gravity": np.random.rand(),
            "mesh_scale_factor": np.random.rand(),
            "eps1": np.random.rand(),
            "eps2": np.random.rand(),
            "w_upstream": np.random.rand(),
            "w_newton": np.random.rand(),
            "derivative_factor": np.random.rand(),
        },
        "extra_options": {
            k + 1: v for k, v in enumerate(np.random.randint(10, size=24))
        },
        "default": {"initial_condition": np.random.rand(num_pvars)},
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(parameters_ref["options"], parameters["options"], atol=1.0e-5)
    helpers.allclose_dict(parameters_ref["extra_options"], parameters["extra_options"])
    if "initial_condition" in parameters["default"].keys():
        assert np.allclose(
            parameters_ref["default"]["initial_condition"],
            parameters["default"]["initial_condition"],
            atol=1.0e-5,
        )
    else:
        assert not len(parameters_ref["default"]["initial_condition"])


@pytest.mark.parametrize(
    "write_read, num_floats",
    [
        (write_read_tough, None),
        (write_read_tough, 8),
        (write_read_json, None),
        (write_read_json, 8),
    ],
)
def test_selec(write_read, num_floats):
    parameters_ref = {
        "selections": {
            "integers": {
                k + 1: v for k, v in enumerate(np.random.randint(100, size=16))
            },
            "floats": (
                np.random.rand(num_floats)
                if num_floats is not None and num_floats <= 8
                else np.random.rand(
                    np.random.randint(100) + 1, np.random.randint(8) + 1
                )
            ),
        },
    }
    parameters_ref["selections"]["integers"][1] = (
        len(parameters_ref["selections"]["floats"])
        if np.ndim(parameters_ref["selections"]["floats"]) == 2
        else 1
    )
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(
        parameters_ref["selections"]["integers"], parameters["selections"]["integers"]
    )
    if "floats" in parameters["selections"].keys():
        assert np.allclose(
            parameters_ref["selections"]["floats"],
            parameters["selections"]["floats"],
            atol=1.0e-4,
        )
    else:
        assert parameters_ref["selections"]["integers"][1] == 0


@pytest.mark.parametrize(
    "write_read, num_pvars, num_items",
    [
        (write_read_tough, 4, None),
        (write_read_tough, 6, None),
        (write_read_tough, 4, 1),
        (write_read_tough, 6, 1),
        (write_read_json, 4, None),
        (write_read_json, 6, None),
    ],
)
def test_indom(write_read, num_pvars, num_items):
    num_items = num_items if num_items else np.random.randint(10) + 1
    parameters_ref = {
        "rocks": {
            helpers.random_string(5): {
                "initial_condition": np.random.rand(num_pvars),
            }
            for _ in range(num_items)
        },
    }
    parameters = write_read(parameters_ref)

    for k, v in parameters_ref["rocks"].items():
        assert np.allclose(
            v["initial_condition"],
            parameters["rocks"][k]["initial_condition"],
            atol=1.0e-4,
        )


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_momop(write_read):
    parameters_ref = {
        "more_options": {
            k + 1: v for k, v in enumerate(np.random.randint(10, size=40))
        },
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(parameters_ref["more_options"], parameters["more_options"])


@pytest.mark.parametrize(
    "write_read, times",
    [
        (write_read_tough, np.random.rand(np.random.randint(100) + 1)),
        (write_read_json, np.random.rand(np.random.randint(100) + 1)),
    ],
)
def test_times(write_read, times):
    parameters_ref = {"times": times}
    parameters = write_read(parameters_ref)

    assert np.allclose(parameters_ref["times"], parameters["times"], atol=1.0e-5)


@pytest.mark.parametrize(
    "write_read, oft, n",
    [
        (write_read_tough, "element_history", 5),
        (write_read_tough, "connection_history", 10),
        (write_read_tough, "generator_history", 5),
        (write_read_json, "element_history", 5),
        (write_read_json, "connection_history", 10),
        (write_read_json, "generator_history", 5),
    ],
)
def test_oft(write_read, oft, n):
    parameters_ref = {
        oft: [helpers.random_string(n) for _ in range(np.random.randint(10) + 1)]
    }
    parameters = write_read(parameters_ref)

    assert parameters_ref[oft] == parameters[oft]


@pytest.mark.parametrize(
    "write_read, specific_enthalpy, label_length",
    [
        (write_read_tough, True, 5),
        (write_read_json, True, 5),
        (write_read_tough, True, 6),
        (write_read_json, True, 6),
        (write_read_tough, False, 5),
        (write_read_json, False, 5),
        (write_read_tough, False, 6),
        (write_read_json, False, 6),
    ],
)
def test_gener(write_read, specific_enthalpy, label_length):
    n_rnd = np.random.randint(100) + 2
    parameters_ref = {
        "generators": [
            {
                "label": helpers.random_label(label_length),
                "name": helpers.random_string(5),
                "nseq": np.random.randint(10),
                "nadd": np.random.randint(10),
                "nads": np.random.randint(10),
                "type": helpers.random_string(4),
                "rates": np.random.rand(),
                "specific_enthalpy": np.random.rand(),
                "layer_thickness": np.random.rand(),
            },
            {
                "label": helpers.random_label(label_length),
                "nseq": np.random.randint(10),
                "nadd": np.random.randint(10),
                "nads": np.random.randint(10),
                "type": helpers.random_string(4),
                "times": np.random.rand(n_rnd),
                "rates": np.random.rand(n_rnd),
                "specific_enthalpy": np.random.rand(n_rnd),
                "layer_thickness": np.random.rand(),
            },
        ],
    }
    parameters = write_read(parameters_ref)

    assert len(parameters_ref["generators"]) == len(parameters["generators"])

    for generator_ref, generator in zip(
        parameters_ref["generators"], parameters["generators"]
    ):
        for k, v in generator_ref.items():
            if k in {"label", "name", "type"}:
                assert v == generator[k]

            else:
                assert np.allclose(v, generator[k], atol=1.0e-4)


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_gener_delv(write_read):
    n_rnd = np.random.randint(10) + 2
    parameters_ref = {
        "generators": [
            {
                "label": helpers.random_label(5),
                "name": helpers.random_string(5),
                "nseq": np.random.randint(10),
                "nadd": np.random.randint(10),
                "nads": np.random.randint(10),
                "type": "DELV",
                "rates": np.random.rand(),
                "specific_enthalpy": np.random.rand(),
                "layer_thickness": np.random.rand(),
            }
            for _ in range(n_rnd)
        ],
    }
    parameters_ref["generators"][0]["n_layer"] = n_rnd
    parameters = write_read(parameters_ref)

    assert len(parameters_ref["generators"]) == len(parameters["generators"])

    for generator_ref, generator in zip(
        parameters_ref["generators"], parameters["generators"]
    ):
        for k, v in generator_ref.items():
            if k in {"label", "name", "type"}:
                assert v == generator[k]

            else:
                assert np.allclose(v, generator[k], atol=1.0e-4)


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_diffu(write_read):
    n_phase = np.random.randint(8) + 1
    parameters_ref = {
        "n_phase": n_phase,
        "diffusion": np.random.rand(np.random.randint(5) + 1, n_phase),
    }
    parameters = write_read(parameters_ref)

    assert np.allclose(
        parameters_ref["diffusion"], parameters["diffusion"], atol=1.0e-4
    )


@pytest.mark.parametrize(
    "write_read, fmt",
    [
        (write_read_tough, None),
        (write_read_tough, helpers.random_string(20)),
        (write_read_json, None),
        (write_read_json, helpers.random_string(20)),
    ],
)
def test_outpu(write_read, fmt):
    parameters_ref = {
        "output": {
            "format": fmt,
            "variables": [
                {"name": helpers.random_string(20)},
                {"name": helpers.random_string(20), "options": None},
                {"name": helpers.random_string(20), "options": np.random.randint(10)},
                {
                    "name": helpers.random_string(20),
                    "options": np.random.randint(10, size=1),
                },
                {
                    "name": helpers.random_string(20),
                    "options": np.random.randint(10, size=2),
                },
            ],
        },
    }
    parameters = write_read(parameters_ref)

    for variable_ref, variable in zip(
        parameters_ref["output"]["variables"], parameters["output"]["variables"]
    ):
        assert variable_ref["name"] == variable["name"]

        if "options" in variable_ref and variable_ref["options"] is not None:
            assert np.allclose(variable_ref["options"], variable["options"])


@pytest.mark.parametrize(
    "write_read, label_length, coord",
    [
        (write_read_tough, 5, False),
        (write_read_json, 5, False),
        (write_read_tough, 6, False),
        (write_read_json, 6, False),
        (write_read_tough, 5, True),
        (write_read_json, 5, True),
        (write_read_tough, 6, True),
        (write_read_json, 6, True),
    ],
)
def test_eleme(write_read, label_length, coord):
    labels = [
        helpers.random_label(label_length) for _ in range(np.random.randint(10) + 1)
    ]
    keys = [
        "nseq",
        "nadd",
        "material",
        "volume",
        "heat_exchange_area",
        "permeability_modifier",
        "center",
    ]
    parameters_ref = {
        "elements": {
            label: {
                key: (
                    np.random.randint(10)
                    if key in {"nseq", "nadd"}
                    else helpers.random_string(5)
                    if key == "material"
                    else np.random.rand(3)
                    if key == "center"
                    else np.random.rand()
                )
                for key in keys
            }
            for label in labels
        },
        "coordinates": coord,
    }
    parameters = write_read(parameters_ref)

    assert sorted(parameters_ref["elements"].keys()) == sorted(
        parameters["elements"].keys()
    )

    for k, v in parameters_ref["elements"].items():
        for kk, vv in v.items():
            if not isinstance(vv, str):
                assert np.allclose(vv, parameters["elements"][k][kk], atol=1.0e-3)
            else:
                assert vv == parameters["elements"][k][kk]

    assert parameters_ref["coordinates"] == parameters["coordinates"]


@pytest.mark.parametrize(
    "write_read, label_length",
    [
        (write_read_tough, 5),
        (write_read_json, 5),
        (write_read_tough, 6),
        (write_read_json, 6),
    ],
)
def test_conne(write_read, label_length):
    labels = [
        "".join(helpers.random_label(label_length) for _ in range(2))
        for _ in range(np.random.randint(10) + 1)
    ]
    keys = [
        "nseq",
        "nadd",
        "permeability_direction",
        "nodal_distances",
        "interface_area",
        "gravity_cosine_angle",
        "radiant_emittance_factor",
    ]
    parameters_ref = {
        "connections": {
            label: {
                key: (
                    np.random.randint(10)
                    if key == "nseq"
                    else np.random.randint(10, size=2)
                    if key == "nadd"
                    else np.random.randint(1, 4)
                    if key == "permeability_direction"
                    else np.random.rand(2)
                    if key == "nodal_distances"
                    else np.random.rand()
                )
                for key in keys
            }
            for label in labels
        }
    }
    parameters = write_read(parameters_ref)

    assert sorted(parameters_ref["connections"].keys()) == sorted(
        parameters["connections"].keys()
    )

    for k, v in parameters_ref["connections"].items():
        for kk, vv in v.items():
            assert np.allclose(vv, parameters["connections"][k][kk], atol=1.0e-4)


@pytest.mark.parametrize(
    "write_read, label_length, num_pvars, num_items",
    [
        (write_read_tough, 5, 4, None),
        (write_read_tough, 5, 6, None),
        (write_read_tough, 6, 4, None),
        (write_read_tough, 5, 4, 1),
        (write_read_tough, 5, 6, 1),
        (write_read_json, 5, 4, None),
        (write_read_json, 5, 6, None),
        (write_read_json, 6, 4, None),
    ],
)
def test_incon(write_read, label_length, num_pvars, num_items):
    num_items = num_items if num_items else np.random.randint(10) + 1
    labels = [helpers.random_label(label_length) for _ in range(num_items)]
    keys = [
        "porosity",
        "userx",
        "values",
    ]
    parameters_ref = {
        "initial_conditions": {
            label: {
                key: (
                    np.random.rand()
                    if key == "porosity"
                    else np.random.rand(np.random.randint(5) + 1)
                    if key == "userx"
                    else np.random.rand(num_pvars)
                )
                for key in keys
            }
            for label in labels
        }
    }
    parameters = write_read(parameters_ref)

    assert sorted(parameters_ref["initial_conditions"].keys()) == sorted(
        parameters["initial_conditions"].keys()
    )

    for k, v in parameters_ref["initial_conditions"].items():
        for kk, vv in v.items():
            assert np.allclose(vv, parameters["initial_conditions"][k][kk], atol=1.0e-3)


def test_meshm_xyz():
    parameters_ref = {
        "meshmaker": {
            "type": "xyz",
            "parameters": [
                {
                    "type": "nx",
                    "n_increment": np.random.randint(100) + 1,
                    "sizes": np.random.rand(),
                },
                {
                    "type": "ny",
                    "sizes": np.random.rand(np.random.randint(100) + 1),
                },
                {
                    "type": "nz",
                    "sizes": np.random.rand(np.random.randint(100) + 1),
                },
                {
                    "type": "nx",
                    "sizes": np.random.rand(np.random.randint(100) + 1),
                },
            ],
            "angle": np.random.rand(),
        }
    }
    parameters = write_read(parameters_ref)

    assert parameters_ref["meshmaker"]["type"] == parameters["meshmaker"]["type"]
    assert np.allclose(
        parameters_ref["meshmaker"]["angle"],
        parameters["meshmaker"]["angle"],
        atol=1.0e-4,
    )
    assert len(parameters_ref["meshmaker"]["parameters"]) == len(
        parameters_ref["meshmaker"]["parameters"]
    )

    for parameter_ref, parameter in zip(
        parameters_ref["meshmaker"]["parameters"], parameters["meshmaker"]["parameters"]
    ):
        for k, v in parameter_ref.items():
            if isinstance(v, str):
                assert v == parameter[k]

            else:
                assert np.allclose(v, parameter[k], atol=1.0e-4)


@pytest.mark.parametrize("layer", [True, False])
def test_meshm_rz2d(layer):
    parameters_ref = {
        "meshmaker": {
            "type": "rz2dl" if layer else "rz2d",
            "parameters": [
                {
                    "type": "radii",
                    "radii": np.random.rand(np.random.randint(100) + 1),
                },
                {
                    "type": "equid",
                    "n_increment": np.random.randint(100) + 1,
                    "size": np.random.rand(),
                },
                {
                    "type": "logar",
                    "n_increment": np.random.randint(100) + 1,
                    "radius": np.random.rand(),
                    "radius_ref": np.random.rand(),
                },
                {
                    "type": "layer",
                    "thicknesses": np.random.rand(np.random.randint(100) + 1),
                },
            ],
        }
    }
    parameters = write_read(parameters_ref)

    assert parameters_ref["meshmaker"]["type"] == parameters["meshmaker"]["type"]
    assert len(parameters_ref["meshmaker"]["parameters"]) == len(
        parameters_ref["meshmaker"]["parameters"]
    )

    for parameter_ref, parameter in zip(
        parameters_ref["meshmaker"]["parameters"], parameters["meshmaker"]["parameters"]
    ):
        for k, v in parameter_ref.items():
            if isinstance(v, str):
                assert v == parameter[k]

            else:
                assert np.allclose(v, parameter[k], atol=1.0e-4)


def test_tmvoc():
    parameters_ref = {
        "eos": "tmvoc",
        "n_component": 1,
        "n_phase": 1,
        "default": {
            "phase_composition": np.random.randint(10),
        },
        "rocks": {
            helpers.random_string(5): {
                "initial_condition": np.random.rand(4),
                "phase_composition": np.random.randint(10),
            }
            for _ in range(np.random.randint(10) + 1)
        },
        "initial_conditions": {
            helpers.random_string(5): {
                "values": np.random.rand(4),
                "phase_composition": np.random.randint(10),
            }
            for _ in range(np.random.randint(10) + 1)
        },
    }
    parameters = write_read(
        parameters_ref,
        writer_kws={"eos": "tmvoc"},
        reader_kws={"eos": "tmvoc"},
    )

    helpers.allclose_dict(parameters_ref["default"], parameters["default"])

    assert sorted(parameters_ref["rocks"].keys()) == sorted(parameters["rocks"].keys())
    for k, v in parameters_ref["rocks"].items():
        helpers.allclose_dict(v, parameters["rocks"][k])

    assert sorted(parameters_ref["initial_conditions"].keys()) == sorted(
        parameters["initial_conditions"].keys()
    )
    for k, v in parameters_ref["initial_conditions"].items():
        helpers.allclose_dict(v, parameters["initial_conditions"][k])


@pytest.mark.parametrize(
    "write_read, flag, enable",
    [
        (write_read_tough, "start", True),
        (write_read_tough, "start", False),
        (write_read_tough, "nover", True),
        (write_read_tough, "nover", False),
        (write_read_json, "start", True),
        (write_read_json, "start", False),
        (write_read_json, "nover", True),
        (write_read_json, "nover", False),
    ],
)
def test_flag(write_read, flag, enable):
    parameters_ref = {flag: enable}
    parameters = write_read(parameters_ref)

    if flag in parameters.keys():
        assert parameters_ref[flag] == parameters[flag]
    else:
        assert not enable
