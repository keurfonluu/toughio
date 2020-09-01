import numpy
import pytest

import helpers
import toughio

write_read = lambda x, **kwargs: helpers.write_read(
    "INFILE", x, toughio.write_input, toughio.read_input, **kwargs
)

write_read_tough = lambda x: write_read(
    x, writer_kws={"file_format": "tough"}, reader_kws={"file_format": "tough"},
)

write_read_json = lambda x: write_read(
    x, writer_kws={"file_format": "json"}, reader_kws={"file_format": "json"},
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
            else [helpers.random_string(80) for _ in range(numpy.random.randint(5) + 2)]
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
            helpers.random_string(5): {key: numpy.random.rand() for key in keys[:5]},
            helpers.random_string(5): {
                key: numpy.random.rand()
                if key != "permeability"
                else numpy.random.rand(3)
                for key in keys[:5]
            },
            helpers.random_string(5): {key: numpy.random.rand() for key in keys},
            helpers.random_string(5): {key: numpy.random.rand() for key in keys},
            helpers.random_string(5): {key: numpy.random.rand() for key in keys},
            helpers.random_string(5): {key: numpy.random.rand() for key in keys},
        }
    }
    names = list(parameters_ref["rocks"].keys())
    parameters_ref["rocks"][names[-1]].update(
        {
            "relative_permeability": {
                "id": numpy.random.randint(10),
                "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
            },
        }
    )
    parameters_ref["rocks"][names[-2]].update(
        {
            "capillarity": {
                "id": numpy.random.randint(10),
                "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
            },
        }
    )
    parameters_ref["rocks"][names[-3]].update(
        {
            "relative_permeability": {
                "id": numpy.random.randint(10),
                "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
            },
            "capillarity": {
                "id": numpy.random.randint(10),
                "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
            },
        }
    )
    parameters = write_read(parameters_ref)

    assert sorted(parameters_ref["rocks"].keys()) == sorted(parameters["rocks"].keys())

    for k, v in parameters_ref["rocks"].items():
        for kk, vv in v.items():
            if not isinstance(vv, dict):
                assert numpy.allclose(vv, parameters["rocks"][k][kk], atol=1.0e-5)
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
            "id": numpy.random.randint(10),
            "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
        }
    if rpcap in {"cap", "both"}:
        parameters_ref["default"]["capillarity"] = {
            "id": numpy.random.randint(10),
            "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
        }
    parameters = write_read(parameters_ref)

    for k, v in parameters_ref["default"].items():
        helpers.allclose_dict(v, parameters["default"][k], atol=1.0e-4)


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_flac(write_read):
    parameters_ref = {
        "flac": {
            "creep": bool(numpy.random.randint(2)),
            "porosity_model": numpy.random.randint(10),
            "version": numpy.random.randint(10),
        },
        "rocks": {
            helpers.random_string(5): {
                "permeability_model": {
                    "id": numpy.random.randint(10),
                    "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
                },
                "equivalent_pore_pressure": {
                    "id": numpy.random.randint(10),
                    "parameters": numpy.random.rand(numpy.random.randint(7) + 1),
                },
            }
            for _ in numpy.random.rand(10) + 1
        },
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(parameters_ref["flac"], parameters["flac"])
    for k, v in parameters_ref["rocks"].items():
        for kk, vv in v.items():
            helpers.allclose_dict(vv, parameters["rocks"][k][kk], atol=1.0e-4)


@pytest.mark.parametrize(
    "write_read, isothermal", [(write_read_tough, True), (write_read_tough, False)],
)
def test_multi(write_read, isothermal):
    import random
    from toughio._io.input.tough._common import eos

    parameters_ref = {
        "eos": random.choice(
            [k for k in eos.keys() if k not in {"eos7", "eos8", "eos9"}]
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
def test_selec(write_read):
    parameters_ref = {
        "selections": {
            "integers": {
                k + 1: v for k, v in enumerate(numpy.random.randint(100, size=16))
            },
            "floats": numpy.random.rand(numpy.random.randint(100)),
        },
    }
    parameters_ref["selections"]["integers"][1] = (
        len(parameters_ref["selections"]["floats"]) - 1
    ) // 8 + 1
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(
        parameters_ref["selections"]["integers"], parameters["selections"]["integers"]
    )
    if "floats" in parameters["selections"].keys():
        assert numpy.allclose(
            parameters_ref["selections"]["floats"],
            parameters["selections"]["floats"],
            atol=1.0e-4,
        )
    else:
        assert parameters_ref["selections"]["integers"][1] == 0


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_solvr(write_read):
    parameters_ref = {
        "solver": {
            "method": numpy.random.randint(10),
            "z_precond": helpers.random_string(2),
            "o_precond": helpers.random_string(2),
            "rel_iter_max": numpy.random.rand(),
            "eps": numpy.random.rand(),
        },
    }
    parameters = write_read(parameters_ref)

    assert parameters_ref["solver"]["method"] == parameters["solver"]["method"]
    assert parameters_ref["solver"]["z_precond"] == parameters["solver"]["z_precond"]
    assert parameters_ref["solver"]["o_precond"] == parameters["solver"]["o_precond"]
    assert numpy.allclose(
        parameters_ref["solver"]["rel_iter_max"],
        parameters["solver"]["rel_iter_max"],
        atol=1.0e-5,
    )
    assert numpy.allclose(
        parameters_ref["solver"]["eps"], parameters["solver"]["eps"], atol=1.0e-5
    )


@pytest.mark.parametrize(
    "write_read, t_steps, num_pvars",
    [
        (write_read_tough, numpy.random.rand(), 4),
        (write_read_tough, numpy.random.rand(numpy.random.randint(100) + 1), 4),
        (write_read_tough, numpy.random.rand(numpy.random.randint(100) + 1), 6),
        (write_read_json, numpy.random.rand(), 4),
        (write_read_json, numpy.random.rand(numpy.random.randint(100) + 1), 4),
        (write_read_json, numpy.random.rand(numpy.random.randint(100) + 1), 6),
    ],
)
def test_param(write_read, t_steps, num_pvars):
    parameters_ref = {
        "options": {
            "n_iteration": numpy.random.randint(10),
            "n_cycle": numpy.random.randint(10),
            "n_second": numpy.random.randint(10),
            "n_cycle_print": numpy.random.randint(10),
            "verbosity": numpy.random.randint(10),
            "temperature_dependence_gas": numpy.random.rand(),
            "effective_strength_vapor": numpy.random.rand(),
            "t_ini": numpy.random.rand(),
            "t_max": numpy.random.rand(),
            "t_steps": t_steps,
            "t_step_max": numpy.random.rand(),
            "t_reduce_factor": numpy.random.rand(),
            "gravity": numpy.random.rand(),
            "mesh_scale_factor": numpy.random.rand(),
            "eps1": numpy.random.rand(),
            "eps2": numpy.random.rand(),
            "w_upstream": numpy.random.rand(),
            "w_newton": numpy.random.rand(),
            "derivative_factor": numpy.random.rand(),
        },
        "extra_options": {
            k + 1: v for k, v in enumerate(numpy.random.randint(10, size=24))
        },
        "default": {"initial_condition": numpy.random.rand(num_pvars)},
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(parameters_ref["options"], parameters["options"], atol=1.0e-5)
    helpers.allclose_dict(parameters_ref["extra_options"], parameters["extra_options"])
    if "initial_condition" in parameters["default"].keys():
        assert numpy.allclose(
            parameters_ref["default"]["initial_condition"],
            parameters["default"]["initial_condition"],
            atol=1.0e-5,
        )
    else:
        assert not len(parameters_ref["default"]["initial_condition"])


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
    num_items = num_items if num_items else numpy.random.randint(10) + 1
    parameters_ref = {
        "rocks": {
            helpers.random_string(5): {
                "initial_condition": numpy.random.rand(num_pvars),
            }
            for _ in range(num_items)
        },
    }
    parameters = write_read(parameters_ref)

    for k, v in parameters_ref["rocks"].items():
        assert numpy.allclose(
            v["initial_condition"],
            parameters["rocks"][k]["initial_condition"],
            atol=1.0e-4,
        )


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_momop(write_read):
    parameters_ref = {
        "more_options": {
            k + 1: v for k, v in enumerate(numpy.random.randint(10, size=40))
        },
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(parameters_ref["more_options"], parameters["more_options"])


@pytest.mark.parametrize(
    "write_read, times",
    [
        (write_read_tough, numpy.random.rand()),
        (write_read_tough, numpy.random.rand(numpy.random.randint(100) + 1)),
        (write_read_json, numpy.random.rand()),
        (write_read_json, numpy.random.rand(numpy.random.randint(100) + 1)),
    ],
)
def test_times(write_read, times):
    parameters_ref = {"times": times}
    parameters = write_read(parameters_ref)

    assert numpy.allclose(parameters_ref["times"], parameters["times"], atol=1.0e-5)


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
        oft: [helpers.random_string(n) for _ in range(numpy.random.randint(10) + 1)]
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
    n_rnd = numpy.random.randint(100) + 1
    parameters_ref = {
        "generators": {
            helpers.random_label(label_length): {
                "name": [
                    helpers.random_string(5),
                    helpers.random_string(5),
                    helpers.random_string(5),
                ],
                "nseq": numpy.random.randint(10, size=3),
                "nadd": numpy.random.randint(10, size=3),
                "nads": numpy.random.randint(10, size=3),
                "type": [
                    helpers.random_string(4),
                    helpers.random_string(4),
                    helpers.random_string(4),
                ],
                "times": [numpy.random.rand(10), None, numpy.random.rand(n_rnd)],
                "rates": [
                    numpy.random.rand(10),
                    numpy.random.rand(),
                    numpy.random.rand(n_rnd),
                ],
                "specific_enthalpy": [
                    numpy.random.rand(10),
                    numpy.random.rand(),
                    numpy.random.rand(n_rnd),
                ]
                if specific_enthalpy
                else None,
                "layer_thickness": numpy.random.rand(3),
            },
            helpers.random_label(label_length): {
                "name": [helpers.random_string(5), helpers.random_string(5)],
                "nseq": numpy.random.randint(10, size=2),
                "nadd": numpy.random.randint(10, size=2),
                "nads": numpy.random.randint(10, size=2),
                "type": [helpers.random_string(4), helpers.random_string(4)],
                "rates": numpy.random.rand(2),
            },
            helpers.random_label(label_length): {
                "nseq": numpy.random.randint(10),
                "nadd": numpy.random.randint(10),
                "nads": numpy.random.randint(10),
                "type": helpers.random_string(4),
                "rates": numpy.random.rand(),
                "layer_thickness": numpy.random.rand(),
            },
        },
    }
    parameters = write_read(parameters_ref)

    assert sorted(parameters_ref["generators"].keys()) == sorted(
        parameters["generators"].keys()
    )

    for k, v in parameters_ref["generators"].items():
        for kk, vv in v.items():
            if kk in {"name", "type"}:
                assert vv == parameters["generators"][k][kk]
            else:
                if kk == "specific_enthalpy" and not specific_enthalpy:
                    continue
                if numpy.ndim(vv):
                    for i, arr_ref in enumerate(vv):
                        arr = parameters["generators"][k][kk][i]
                        if arr_ref is not None:
                            assert numpy.allclose(arr, arr_ref, atol=1.0e-4)
                        else:
                            assert arr is None
                else:
                    assert numpy.allclose(
                        vv, parameters["generators"][k][kk], atol=1.0e-4
                    )


@pytest.mark.parametrize("write_read", [write_read_tough, write_read_json])
def test_diffu(write_read):
    n_phase = numpy.random.randint(8) + 1
    parameters_ref = {
        "n_phase": n_phase,
        "diffusion": numpy.random.rand(numpy.random.randint(5) + 1, n_phase),
    }
    parameters = write_read(parameters_ref)

    assert numpy.allclose(
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
            "variables": {
                helpers.random_string(20): None,
                helpers.random_string(20): [numpy.random.randint(10)],
                helpers.random_string(20): [
                    numpy.random.randint(10),
                    numpy.random.randint(10),
                ],
            },
        },
    }
    parameters = write_read(parameters_ref)

    helpers.allclose_dict(
        parameters_ref["output"]["variables"], parameters["output"]["variables"]
    )


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
        helpers.random_label(label_length) for _ in range(numpy.random.randint(10) + 1)
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
                    numpy.random.randint(10)
                    if key in {"nseq", "nadd"}
                    else helpers.random_string(5)
                    if key == "material"
                    else numpy.random.rand(3)
                    if key == "center"
                    else numpy.random.rand()
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
                assert numpy.allclose(vv, parameters["elements"][k][kk], atol=1.0e-4)
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
        for _ in range(numpy.random.randint(10) + 1)
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
                    numpy.random.randint(10)
                    if key == "nseq"
                    else numpy.random.randint(10, size=2)
                    if key == "nadd"
                    else numpy.random.randint(1, 4)
                    if key == "permeability_direction"
                    else numpy.random.rand(2)
                    if key == "nodal_distances"
                    else numpy.random.rand()
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
            assert numpy.allclose(vv, parameters["connections"][k][kk], atol=1.0e-4)


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
    num_items = num_items if num_items else numpy.random.randint(10) + 1
    labels = [
        helpers.random_label(label_length) for _ in range(num_items)
    ]
    keys = [
        "porosity",
        "userx",
        "values",
    ]
    parameters_ref = {
        "initial_conditions": {
            label: {
                key: (
                    numpy.random.rand()
                    if key == "porosity"
                    else numpy.random.rand(numpy.random.randint(5) + 1)
                    if key == "userx"
                    else numpy.random.rand(num_pvars)
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
            assert numpy.allclose(
                vv, parameters["initial_conditions"][k][kk], atol=1.0e-3
            )


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
