import pytest
import numpy as np
import toughio


@pytest.fixture(params=["tough", "json"], ids=["tough", "json"])
def file_format(request):
    return request.param

@pytest.fixture
def write_read(file_format, helpers):
    def _write_read(x, writer_kws=None, reader_kws=None, **kwargs):
        writer_kws_ = {"file_format": file_format}
        reader_kws_ = {"file_format": file_format}
        writer_kws_.update(writer_kws if writer_kws is not None else {})
        reader_kws_.update(reader_kws if reader_kws is not None else {})

        return helpers.write_read(
            "INFILE",
            x,
            toughio.write_input,
            toughio.read_input,
            writer_kws=writer_kws_,
            reader_kws=reader_kws_,
            **kwargs,
        )
    return _write_read

@pytest.mark.parametrize("flag, enable", [
    ("index", True), ("index", False),
    ("start", True), ("start", False),
    ("nover", True), ("nover", False),
])
def test_flag(write_read, flag, enable):
    parameters_ref = {flag: enable}
    parameters = write_read(parameters_ref)
    if flag in parameters:
        assert parameters_ref[flag] == parameters[flag]
    else:
        assert not enable

@pytest.mark.parametrize("single", [True, False])
def test_title(write_read, single, helpers):
    parameters_ref = {
        "title": (
            helpers.random_string(80)
            if single
            else [helpers.random_string(80) for _ in range(np.random.randint(5) + 2)]
        ),
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters)

@pytest.mark.parametrize("single", [True, False])
def test_end_comments(write_read, single, helpers):
    parameters_ref = {
        "end_comments": (
            helpers.random_string(80)
            if single
            else [helpers.random_string(80) for _ in range(np.random.randint(5) + 2)]
        ),
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters)

@pytest.mark.parametrize("t_steps,num_pvars", [
    (lambda: np.random.rand(), 4),
    (lambda: np.random.rand(np.random.randint(100) + 1), 4),
    (lambda: np.random.rand(np.random.randint(100) + 1), 10),
])
def test_param(write_read, t_steps, num_pvars, helpers):
    t_steps = t_steps() if callable(t_steps) else t_steps
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
        "extra_options": {k + 1: v for k, v in enumerate(np.random.randint(10, size=24))},
        "default": {"initial_condition": np.random.rand(num_pvars)},
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("isothermal", [True, False])
def test_multi(write_read, isothermal, file_format, helpers):
    import random
    from toughio._io.input.tough.blocks.multi import eos_values as eos
    if file_format == "json":
        pytest.skip("MULTI block not supported for JSON format")
    parameters_ref = {
        "eos": random.choice(
            [k for k in eos if k not in {"eos7", "eos8", "eos9", "tmvoc"}]
        ),
        "isothermal": isothermal,
    }
    parameters = write_read(parameters_ref)
    multi_ref = eos[parameters_ref["eos"]]
    multi = [
        parameters["n_component"],
        parameters["n_component"] + 1,
        parameters["n_phase"],
        6,
    ]
    assert helpers.allclose(parameters_ref, parameters, ignore_keys=["eos"])
    assert helpers.allclose(multi_ref, multi)

@pytest.mark.parametrize("n_phase", [lambda: np.random.randint(8) + 1])
def test_diffu(write_read, n_phase, helpers):
    n_phase = n_phase() if callable(n_phase) else n_phase
    parameters_ref = {
        "n_phase": n_phase,
        "diffusion": np.random.rand(np.random.randint(5) + 1, n_phase),
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("times_len", [lambda: np.random.randint(100) + 1])
def test_times(write_read, times_len, helpers):
    times_len = times_len() if callable(times_len) else times_len
    parameters_ref = {"times": np.random.rand(times_len)}
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("oft, n", [
    ("element_history", 5),
    ("connection_history", 10),
    ("generator_history", 5),
])
def test_oft(write_read, oft, n, file_format, helpers):
    parameters_ref = {
        oft: [
            helpers.random_string(n),
            helpers.random_string(n),
            {"label": helpers.random_string(n)},
            {"label": helpers.random_string(n), "flag": np.random.randint(10)},
        ]
    }
    parameters = write_read(parameters_ref)
    if file_format != "json":
        for i, v in enumerate(parameters_ref[oft]):
            if not isinstance(v, dict):
                parameters_ref[oft][i] = {"label": v}
    assert helpers.allclose(parameters_ref, parameters)

@pytest.mark.parametrize("n_roft", [lambda: np.random.randint(10) + 1])
def test_roft(write_read, n_roft, helpers):
    n_roft = n_roft() if callable(n_roft) else n_roft
    parameters_ref = {
        "rock_history": [
            [helpers.random_string(5), helpers.random_string(5)]
            for _ in range(n_roft)
        ]
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters)

@pytest.mark.parametrize("num_floats", [None, 8])
def test_selec(write_read, num_floats, helpers):
    floats = (
        np.random.rand(num_floats)
        if num_floats is not None and num_floats <= 8
        else np.random.rand(np.random.randint(100) + 1, np.random.randint(8) + 1)
    )
    parameters_ref = {
        "selections": {
            "integers": {k + 1: v for k, v in enumerate(np.random.randint(100, size=16))},
            "floats": floats,
        },
    }
    parameters_ref["selections"]["integers"][1] = (
        len(parameters_ref["selections"]["floats"])
        if np.ndim(parameters_ref["selections"]["floats"]) == 2
        else 1
    )
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("array_dim_keys", [
    [
        "n_rocks", "n_times", "n_generators", "n_rates", "n_increment_x", "n_increment_y", "n_increment_z", "n_increment_rad", "n_properties", "n_properties_times", "n_regions", "n_regions_parameters", "n_ltab", "n_rpcap", "n_elements_timbc", "n_timbc"
    ]
])
def test_dimen(write_read, array_dim_keys, helpers):
    parameters_ref = {
        "array_dimensions": {k: np.random.randint(100) for k in array_dim_keys}
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters)

@pytest.mark.parametrize("keys", [[
    "density", "porosity", "permeability", "conductivity", "specific_heat", "compressibility", "expansivity", "conductivity_dry", "tortuosity", "klinkenberg_parameter", "distribution_coefficient_3", "distribution_coefficient_4"
]])
def test_rocks(write_read, keys, helpers):
    parameters_ref = {
        "rocks": {
            helpers.random_string(5): {key: np.random.rand() for key in keys[:5]},
            helpers.random_string(5): {key: np.random.rand() if key != "permeability" else np.random.rand(3) for key in keys[:5]},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
            helpers.random_string(5): {key: np.random.rand() for key in keys},
        }
    }
    names = list(parameters_ref["rocks"])
    parameters_ref["rocks"][names[-1]].update({"relative_permeability": {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)}})
    parameters_ref["rocks"][names[-2]].update({"capillarity": {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)}})
    parameters_ref["rocks"][names[-3]].update({"relative_permeability": {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)}, "capillarity": {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)}})
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("rpcap", ["rp", "cap", "both"])
def test_rpcap(write_read, rpcap, helpers):
    parameters_ref = {"default": {}}
    if rpcap in {"rp", "both"}:
        parameters_ref["default"]["relative_permeability"] = {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)}
    if rpcap in {"cap", "both"}:
        parameters_ref["default"]["capillarity"] = {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)}
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("flac_keys", [["creep", "porosity_model", "version"]])
def test_flac(write_read, flac_keys, helpers):
    parameters_ref = {
        "flac": {k: bool(np.random.randint(2)) if k == "creep" else np.random.randint(10) for k in flac_keys},
        "rocks": {
            helpers.random_string(5): {
                "permeability_model": {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)},
                "equivalent_pore_pressure": {"id": np.random.randint(10), "parameters": np.random.rand(np.random.randint(7) + 1)},
            } for _ in range(int(np.random.rand() * 10) + 1)
        },
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("n_chemp", [10])
def test_chemp(write_read, n_chemp, helpers):
    parameters_ref = {
        "chemical_properties": {
            helpers.random_string(20): {k: np.random.rand() for k in [
                "temperature_crit", "pressure_crit", "compressibility_crit", "pitzer_factor", "dipole_moment", "boiling_point", "vapor_pressure_a", "vapor_pressure_b", "vapor_pressure_c", "vapor_pressure_d", "molecular_weight", "heat_capacity_a", "heat_capacity_b", "heat_capacity_c", "heat_capacity_d", "napl_density_ref", "napl_temperature_ref", "gas_diffusivity_ref", "gas_temperature_ref", "exponent", "napl_viscosity_a", "napl_viscosity_b", "napl_viscosity_c", "napl_viscosity_d", "volume_crit", "solubility_a", "solubility_b", "solubility_c", "solubility_d", "oc_coeff", "oc_fraction", "oc_decay"]} for _ in range(int(np.random.rand() * n_chemp) + 1)
        }
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("n_ncgas", [10])
def test_ncgas(write_read, n_ncgas, helpers):
    parameters_ref = {
        "non_condensible_gas": [helpers.random_string(10) for _ in range(int(np.random.rand() * n_ncgas) + 1)]
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters)

@pytest.mark.parametrize("num_pvars,num_items", [
    (4, None), (10, None), (4, 1), (10, 1)
])
def test_indom(write_read, num_pvars, num_items, helpers):
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
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("n_items", [lambda: np.random.randint(10) + 2])
def test_gener_delv(write_read, n_items, helpers):
    n_items = n_items() if callable(n_items) else n_items
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
            for _ in range(n_items)
        ],
    }
    parameters_ref["generators"][0]["n_layer"] = n_items
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("n_items", [lambda: np.random.randint(10) + 2])
def test_timbc(write_read, n_items, helpers):
    n_items = n_items() if callable(n_items) else n_items
    parameters_ref = {
        "boundary_conditions": [
            {
                "label": helpers.random_label(),
                "variable": np.random.randint(6),
                "times": np.random.rand(10),
                "values": np.random.rand(10),
            }
            for _ in range(n_items)
        ],
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-8)

@pytest.mark.parametrize("keys", [[
    "nseq", "nadd", "material", "volume", "heat_exchange_area", "permeability_modifier", "center"
]])
@pytest.mark.parametrize("label_length,coord", [
    (5, False), (6, False), (5, True), (6, True)
])
def test_eleme(write_read, keys, label_length, coord, helpers):
    labels = [helpers.random_label(label_length) for _ in range(np.random.randint(10) + 1)]
    parameters_ref = {
        "elements": {
            label: {
                key: (
                    np.random.randint(10) if key in {"nseq", "nadd"}
                    else (
                        helpers.random_string(5) if key == "material"
                        else np.random.rand(3) if key == "center" else np.random.rand()
                    )
                )
                for key in keys
            }
            for label in labels
        },
        "coordinates": coord,
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-3)

@pytest.mark.parametrize("label_length", [5, 6])
def test_conne(write_read, label_length, helpers):
    labels = ["".join(helpers.random_label(label_length) for _ in range(2)) for _ in range(np.random.randint(10) + 1)]
    keys = [
        "nseq", "nadd", "permeability_direction", "nodal_distances", "interface_area", "gravity_cosine_angle", "radiant_emittance_factor"
    ]
    parameters_ref = {
        "connections": {
            label: {
                key: (
                    np.random.randint(10) if key == "nseq"
                    else (
                        np.random.randint(10, size=2) if key == "nadd"
                        else (
                            np.random.randint(1, 4) if key == "permeability_direction"
                            else (
                                np.random.rand(2) if key == "nodal_distances" else np.random.rand()
                            )
                        )
                    )
                )
                for key in keys
            }
            for label in labels
        }
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("label_length,num_pvars,num_items", [
    (5, 4, None), (5, 10, None), (6, 4, None), (5, 4, 1), (5, 10, 1), (6, 4, None)
])
def test_incon(write_read, label_length, num_pvars, num_items, helpers):
    num_items = num_items if num_items else np.random.randint(10) + 1
    labels = [helpers.random_label(label_length) for _ in range(num_items)]
    keys = ["porosity", "userx", "values"]
    parameters_ref = {
        "initial_conditions": {
            label: {
                key: (
                    np.random.rand() if key == "porosity"
                    else (
                        np.random.rand(np.random.randint(5) + 1) if key == "userx" else np.random.rand(num_pvars)
                    )
                )
                for key in keys
            }
            for label in labels
        }
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-3)

def test_meshm_xyz(write_read, helpers):
    parameters_ref = {
        "meshmaker": {
            "type": "xyz",
            "parameters": [
                {"type": "nx", "n_increment": np.random.randint(100) + 1, "sizes": np.random.rand()},
                {"type": "ny", "sizes": np.random.rand(np.random.randint(100) + 1)},
                {"type": "nz", "sizes": np.random.rand(np.random.randint(100) + 1)},
                {"type": "nx", "sizes": np.random.rand(np.random.randint(100) + 1)},
            ],
            "angle": np.random.rand(),
        }
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("layer, minc", [(True, False), (False, False), (True, True), (False, True)])
def test_meshm_rz2d(write_read, layer, minc, helpers):
    parameters_ref = {
        "meshmaker": {
            "type": "rz2dl" if layer else "rz2d",
            "parameters": [
                {"type": "radii", "radii": np.random.rand(np.random.randint(100) + 1)},
                {"type": "equid", "n_increment": np.random.randint(100) + 1, "size": np.random.rand()},
                {"type": "logar", "n_increment": np.random.randint(100) + 1, "radius": np.random.rand(), "radius_ref": np.random.rand()},
                {"type": "layer", "thicknesses": np.random.rand(np.random.randint(100) + 1)},
            ],
        }
    }
    if minc:
        parameters_ref["minc"] = {
            "type": helpers.random_string(5),
            "dual": helpers.random_string(5),
            "n_minc": np.random.randint(100) + 1,
            "where": helpers.random_string(4),
            "parameters": np.random.rand(7),
            "volumes": np.random.rand(np.random.randint(100) + 1),
        }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

def test_minc(write_read, helpers):
    n_volume = np.random.randint(100) + 1
    parameters_ref = {
        "minc": {
            "type": helpers.random_string(5),
            "dual": helpers.random_string(5),
            "n_minc": np.random.randint(100) + 1,
            "where": helpers.random_string(4),
            "parameters": np.random.rand(7),
            "volumes": np.random.rand(n_volume),
        }
    }
    parameters = write_read(parameters_ref)
    assert helpers.allclose(parameters_ref, parameters, atol=1.0e-4)

@pytest.mark.parametrize("eos", ["eco2m", "tmvoc"])
def test_phase_composition(write_read, file_format, eos, helpers):
    parameters_ref = {
        "eos": eos,
        "n_component": 1,
        "n_phase": 1,
        "default": {"phase_composition": np.random.randint(10)},
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

    reader_kws = {"eos": eos} if file_format != "json" else {}
    parameters = write_read(parameters_ref, reader_kws=reader_kws)
    assert helpers.allclose(parameters_ref, parameters, ignore_keys=["eos"])
