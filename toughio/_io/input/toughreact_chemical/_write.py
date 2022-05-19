from ._helpers import section
from ..._common import to_str
from ...._common import open_file

from ..toughreact_solute._write import _get

__all__ = [
    "write",
]


def write(filename, parameters, verbose=True):
    buffer = write_buffer(parameters, verbose)
    with open_file(filename, "w") as f:
        for record in buffer:
            f.write(record)


def write_buffer(parameters, verbose):
    # Define input file contents
    out = []
    out += _write_title(parameters)
    out += ["# Definition of the geochemical system"] if verbose else []
    out += _write_prim(parameters, verbose)
    out += _write_akin(parameters, verbose)
    out += _write_aque(parameters)
    out += _write_miner(parameters, verbose)
    out += _write_gas(parameters, verbose)
    out += _write_surx(parameters)
    out += _write_kdde(parameters, verbose)
    out += _write_exch(parameters, verbose)
    out += _write_water(parameters, verbose)
    out += _write_imin(parameters, verbose)
    out += _write_igas(parameters, verbose)
    out += _write_zppr(parameters, verbose)
    out += _write_zads(parameters, verbose)
    out += _write_zlkd(parameters, verbose)
    out += _write_zexc(parameters, verbose)
    out += ["# end"]

    return "\n".join(out)


@section("# Title", f"#{'-' * 79}")
def _write_title(parameters):
    """Write title."""
    return [parameters["title"] if "title" in parameters else ""]


@section("# Primary aqueous species")
def _write_prim(parameters, verbose):
    """Write primary species."""
    out = []

    if not ("primary_species" in parameters and parameters["primary_species"]):
        return out

    if verbose:
        item = max(parameters["primary_species"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for specie in parameters["primary_species"]:
        values = [
            _get(specie, "name", "''"),
            _get(specie, "transport", 0),
        ]

        if values[-1] == 2:
            values += [
                _get(specie, "mineral_name", "''"),
                _get(specie, "sorption_density", 0.0),
                _get(specie, "adsorption_id", 0),
            ]

            if values[-1] == 1:
                values += [_get(specie, "capacitance", 0.0)]

        out += _write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

    return out


@section("# Aqueous kinetics")
def _write_akin(parameters, verbose):
    out = []

    if not ("aqueous_kinetics" in parameters and parameters["aqueous_kinetics"]):
        return out

    # Record 2
    out += [f"{len(parameters['aqueous_kinetics'])}"]
    
    for i, kinetic in enumerate(parameters["aqueous_kinetics"]):
        # Record 3
        out += [f"{i + 1}"]

        # Record 4
        n = len(kinetic["aqueous_species"])
        values = [n]
        if n:
            for specie in kinetic["aqueous_species"]:
                values += [
                    _get(specie, "stoichiometric_coeff", 1.0),
                    _get(specie, "name", "''"),
                ]

        if "reaction_affinity" in kinetic:
            values += [
                _get(kinetic, ("reaction_affinity", "id"), 0),
                _get(kinetic, ("reaction_affinity", "cf"), 0.0),
                _get(kinetic, ("reaction_affinity", "logK"), 0.0),
            ]

        out += _write_ffrecord(values)

        # Record 5
        values = [
            _get(kinetic, "id", 0),
            _get(kinetic, "n_mechanism", 0),
        ]
        tmp = _write_ffrecord(values)

        # Record 6
        rate = _get(kinetic, "rate", 0.0)
        rate = rate if not isinstance(rate, dict) else -1.0
        tmp += [f"{rate}"]

        # Record 6.1
        if rate == -1.0:
            values = [
                _get(kinetic, ("rate", "k25"), 0.0),
                _get(kinetic, ("rate", "Ea"), 0.0),
            ]
            tmp += _write_ffrecord(values)

        # Record 7
        ncp_rx1 = len(kinetic["product"])
        values = [ncp_rx1]
        if ncp_rx1:
            for specie in kinetic["product"]:
                values += [
                    _get(specie, "specie", "''"),
                    _get(specie, "flag", 0),
                    _get(specie, "power", 0.0),
                ]
        tmp += _write_ffrecord(values)

        # Record 8
        ncp_rx2 = len(kinetic["monod"])
        values = [ncp_rx2]
        if ncp_rx2:
            for specie in kinetic["monod"]:
                values += [
                    _get(specie, "specie", "''"),
                    _get(specie, "flag", 0),
                    _get(specie, "half_saturation", 0.0),
                ]
        tmp += _write_ffrecord(values)

        # Record 9
        ncp_rx3 = len(kinetic["inhibition"])
        values = [ncp_rx3]
        if ncp_rx3:
            for specie in kinetic["inhibition"]:
                values += [
                    _get(specie, "specie", "''"),
                    _get(specie, "flag", 0),
                    _get(specie, "constant", 0.0),
                ]
        tmp += _write_ffrecord(values)

        # Write records 5 to 9
        if verbose:
            n = max(len(max(tmp, key=len)), 30)
            tmp[0] = f"{tmp[0]:<{n}}  ! Kinetic model index, number of mechanisms"
            tmp[1] = f"{tmp[1]:<{n}}  ! Forward rate constant"
            tmp[-3] = f"{tmp[-3]:<{n}}  ! Species in product term"
            tmp[-2] = f"{tmp[-2]:<{n}}  ! Species in monod terms"
            tmp[-1] = f"{tmp[-1]:<{n}}  ! Species in inhibition terms"

        out += tmp

    return out


@section("# Aqueous complexes")
def _write_aque(parameters):
    """Write aqueous species."""
    out = []

    if not ("aqueous_species" in parameters and parameters["aqueous_species"]):
        return out

    for specie in parameters["aqueous_species"]:
        out += [f"{specie:<20}"]

    return out


@section("# Minerals")
def _write_miner(parameters, verbose):
    out = []

    if not ("minerals" in parameters and parameters["minerals"]):
        return out

    if verbose:
        item = max(parameters["minerals"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for mineral in parameters["minerals"]:
        # Record 2
        ikin = _get(mineral, "type", 0)
        idispre = _get(mineral, "kinetic_constraint", 0)
        values = [
            _get(mineral, "name", "''"),
            ikin,
            idispre,
            _get(mineral, "solid_solution", 0),
            _get(mineral, "precipitation_dry", 0),
        ]
        out += _write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

        # Records 2.1 and 2.2
        if ikin == 1:
            n = 2 if idispre == 3 else 1
            for ir in range(n):
                if idispre == 1:
                    key = "dissolution"

                elif idispre == 2:
                    key = "precipitation"

                elif idispre == 3:
                    key = "dissolution" if ir == 0 else "precipitation"

                idep = _get(mineral, (key, "rate_ph_dependence"), 0)
                values = [
                    _get(mineral, (key, "k25"), 0.0),
                    idep,
                    _get(mineral, (key, "eta"), 0.0),
                    _get(mineral, (key, "theta"), 0.0),
                    _get(mineral, (key, "activation_energy"), 0.0),
                    _get(mineral, (key, "a"), 0.0),
                    _get(mineral, (key, "b"), 0.0),
                    _get(mineral, (key, "c"), 0.0),
                ]

                # Record 2.2
                if key == "precipitation":
                    values += [
                        _get(mineral, (key, "volume_fraction_ini"), 0.0),
                        _get(mineral, (key, "id"), 0),
                    ]
                
                out += _write_ffrecord(values)

                # Record 2.1.1
                if idep == 1:
                    values = [
                        _get(mineral, (key, "ph1"), 0.0),
                        _get(mineral, (key, "slope1"), 0.0),
                        _get(mineral, (key, "ph2"), 0.0),
                        _get(mineral, (key, "slope2"), 0.0),
                    ]
                    out += _write_ffrecord(values)
                
                # Record 2.1.2
                elif idep == 2:
                    ndis = len(mineral[key]["extra_mechanisms"]) if "extra_mechanisms" in mineral[key] else 0
                    values = [ndis]
                    out += _write_ffrecord(values)

                    # Record 2.1.2.1
                    if ndis:
                        for mechanism in mineral[key]["extra_mechanisms"]:
                            values = [
                                _get(mechanism, "ki", 0.0),
                                _get(mechanism, "activation_energy", 0.0),
                            ]

                            nspds = len(mechanism["mechanism"])
                            values += [nspds]
                            if nspds:
                                for mechanism_ in mechanism["mechanism"]:
                                    values += [
                                        _get(mechanism_, "specie", "''"),
                                        _get(mechanism_, "power", 0.0),
                                    ]
                            out += _write_ffrecord(values)

        # Record 2.3
        if idispre != 1:
            values = [
                _get(mineral, "gap", 0.0),
                _get(mineral, "temp1", 0.0),
                _get(mineral, "temp2", 0.0),
            ]
            out += _write_ffrecord(values)

    return out


@section("# Gases")
def _write_gas(parameters, verbose):
    """Write gaseous species."""
    out = []

    if not ("gaseous_species" in parameters and parameters["gaseous_species"]):
        return out

    if verbose:
        item = max(parameters["gaseous_species"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for specie in parameters["gaseous_species"]:
        values = [
            _get(specie, "name", "''"),
            _get(specie, "fugacity", 0),
        ]
        out += _write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

    return out


@section("# Surface complexes")
def _write_surx(parameters):
    """Write surface complexes."""
    out = []

    if not ("surface_complexes" in parameters and parameters["surface_complexes"]):
        return out

    for complex in parameters["surface_complexes"]:
        out += [f"{complex:<20}"]

    return out


@section("# Species with Kd and decay")
def _write_kdde(parameters, verbose):
    """Write Kd and decay."""
    out = []

    if not ("kd_decay" in parameters and parameters["kd_decay"]):
        return out

    if verbose:
        item = max(parameters["kd_decay"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for specie in parameters["kd_decay"]:
        values = [
            _get(specie, "name", "''"),
            _get(specie, "decay_constant", 0.0),
            _get(specie, "a", 0.0),
            _get(specie, "b", 0.0),
        ]
        out += _write_ffrecord(values, verbose, str_fmt=fmt)

    return out


@section("# Exchangeable cations")
def _write_exch(parameters, verbose):
    """Write exchanges species."""
    out = []

    if not ("exchanged_species" in parameters and parameters["exchanged_species"]):
        return out

    # Record 2
    nxsites = len(_get(parameters["exchanged_species"][0], "site_coeffs", []))
    values = [
        nxsites,
        _get(parameters, "exchange_sites_id", 0),
    ]
    out += _write_ffrecord(values, verbose)

    # Record 3
    if verbose:
        item = max(parameters["exchanged_species"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for specie in parameters["exchanged_species"]:
        values = [
            _get(specie, "name", "''"),
            int(_get(specie, "reference", False)),
            _get(specie, "type", 1),
        ]
        values += [*_get(specie, "site_coeffs", [])]
        out += _write_ffrecord(values, verbose, str_fmt=fmt)

    return out


@section("# Initial and injection water types")
def _write_water(parameters, verbose):
    """Write water zones."""
    out = []

    if "zones" not in parameters:
        return out

    nwtypes = {
        "initial_waters": 0,
        "injection_waters": 0,
    }
    for key in nwtypes:
        if key in parameters["zones"]:
            nwtypes[key] = len(parameters["zones"][key])

    if not sum(nwtypes.values()):
        return out

    values = list(nwtypes.values())
    out += _write_ffrecord(values)

    for k, v in nwtypes.items():
        if not v:
            continue

        for i, zone in enumerate(parameters["zones"][k]):
            # Record 4
            if verbose:
                out += ["# ID      T(C)    P(bar)"]

                if "rock" in zone:
                    out[-1] = f"{out[-1]}      Rock"

            values = [
                i + 1 if "rock" not in zone else -1,
                _get(zone, "temperature", 0.0),
                _get(zone, "pressure", 0.0),
            ]
            values += [_get(zone, "rock", "''")[:5]] if "rock" in zone else []
            out += _write_ffrecord(values, verbose, str_fmt="{:>9}")

            # Record 6
            if "species" in zone and zone["species"]:
                if verbose:
                    item = max(zone["species"], key=lambda x: len(x["name"]))
                    n = min(len(item["name"]), 20)
                    fmt1 = f"{{:{n}}}"

                    try:
                        item = max(zone["species"], key=lambda x: len(x["nameq"]))
                        fmt2 = f"{{:>{max(len(item['nameq']), 10)}}}"

                    except KeyError:
                        fmt2 = "{:>10}"

                    out += [f"# {' ' * (n - 2)} icon     guess      ctot {fmt2.format('constraint')}  log(Q/K)"]

                for specie in zone["species"]:
                    name = _get(specie, "name", "''")
                    name = fmt1.format(name) if verbose else name
                    nameq = "*" if "nameq" not in specie else specie["nameq"]
                    values = [
                        _get(specie, "flag", 0),
                        _get(specie, "guess", 0.0),
                        _get(specie, "ctot", 0.0),
                        nameq,  # nameq is optional
                        _get(specie, "log_fugacity", 0.0),
                    ]
                    tmp = _write_ffrecord(values, verbose, str_fmt=fmt2 if verbose else None)
                    out += [f"{name} {tmp[0]}"]

            # Record 7
            out += ["*"]

    return out[:-1]


@section("# Initial mineral zones")
def _write_imin(parameters, verbose):
    """Write mineral zones."""
    out = []

    if "zones" not in parameters:
        return out

    nmtype = 0
    if "minerals" in parameters["zones"]:
        nmtype = len(parameters["zones"]["minerals"])

    if not nmtype:
        return out

    values = [nmtype]
    out += _write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["minerals"]):
        # Record 4
        values = [i + 1] if "rock" not in zone else [-1, f"'{zone['rock'][:5]}'"]
        out += _write_ffrecord(values)

        # Record 6
        if "minerals" in zone and zone["minerals"]:
            if verbose:
                item = max(zone["minerals"], key=lambda x: len(x["name"]))
                fmt = f"{{:{max(len(item['name']), 10)}}}"

            for mineral in zone["minerals"]:
                name = _get(mineral, "name", "''")
                name = fmt.format(name) if verbose else name
                flag = _get(mineral, "flag", 0)
                values = [
                    _get(mineral, "volume_fraction_ini", 0.0),
                    flag,
                ]
                tmp = _write_ffrecord(values, verbose)
                out += [f"{name} {tmp[0]}"]

                # Record 6.1
                if flag == 1:
                    values = [
                        _get(mineral, "radius", 0.0),
                        _get(mineral, "area_ini", 0.0),
                        _get(mineral, "area_unit", 0),
                    ]
                    out += _write_ffrecord(values, verbose)
                    out[-1] = out[-1].lstrip()
                
        # Record 7
        out += ["*"]

    return out[:-1]


@section("# Initial and injection gas zones")
def _write_igas(parameters, verbose):
    """Write gas zones."""
    out = []

    if "zones" not in parameters:
        return out

    ngtypes = {
        "initial_gases": 0,
        "injection_gases": 0,
    }
    for key in ngtypes:
        if key in parameters["zones"]:
            ngtypes[key] = len(parameters["zones"][key])

    if not sum(ngtypes.values()):
        return out

    values = list(ngtypes.values())
    out += _write_ffrecord(values)

    for k, v in ngtypes.items():
        if not v:
            continue

        for i, zone in enumerate(parameters["zones"][k]):
            # Record 4
            values = [i + 1]
            out += _write_ffrecord(values, verbose)

            # Record 6
            if verbose:
                item = max(zone, key=lambda x: len(x["name"]))
                n = min(len(item["name"]), 20)
                fmt = f"{{:{n}}}"

                out += [
                    (
                        f"# {' ' * n} PP(bar)"
                        if k == "initial_gases"
                        else f"# {' ' * (n - 1)} PP(%mol)"
                    )
                ]

            for specie in zone:
                name = _get(specie, "name", "''")
                name = fmt.format(name) if verbose else name
                values = [
                    (
                        _get(specie, "partial_pressure", 0.0)
                        if k == "initial_gases"
                        else _get(specie, "mole_fraction", 0.0)
                    )
                ]
                tmp = _write_ffrecord(values, verbose)
                out += [f"{name} {tmp[0]}"]

            # Record 7
            out += ["*"]

    return out[:-1]


@section("# Permeability-porosity zones")
def _write_zppr(parameters, verbose):
    """Write permeability-porosity law zones."""
    out = []

    if "zones" not in parameters:
        return out

    nppzone = 0
    if "permeability_porosity" in parameters["zones"]:
        nppzone = len(parameters["zones"]["permeability_porosity"])

    if not nppzone:
        return out

    values = [nppzone]
    out += _write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["permeability_porosity"]):
        # Record 4
        values = [i + 1]
        out += _write_ffrecord(values)

        # Record 6
        if verbose:
            out += ["# ID     a-par     b-par"]

        values = [
            _get(zone, "id", 0),
            _get(zone, "a", 0.0),
            _get(zone, "b", 0.0),
        ]
        out += _write_ffrecord(values, verbose)

    return out


@section("# Initial surface adsorption zones")
def _write_zads(parameters, verbose): 
    """Write surface adsorption zones."""
    out = []

    if "zones" not in parameters:
        return out

    ndtype = 0
    if "adsorption" in parameters["zones"]:
        ndtype = len(parameters["zones"]["adsorption"])

    if not ndtype:
        return out

    values = [ndtype]
    out += _write_ffrecord(values)

    # Number of surface primary species
    nsurfs = sum(specie["transport"] == 2 for specie in parameters["primary_species"])

    for i, zone in enumerate(parameters["zones"]["adsorption"]):
        # Record 5
        values = [
            i + 1,
            _get(zone, "flag", 0),
        ]
        out += _write_ffrecord(values)

        # Record 6
        if nsurfs:
            if "species" not in zone:
                raise ValueError()

            elif len(zone["species"]) != nsurfs:
                raise ValueError()

            if verbose:
                item = max(zone["species"], key=lambda x: len(x["name"]))
                n = max(len(item["name"]), 10)
                fmt = f"{{:{n}}}"

                out += [f"# {' ' * (n - 2)} unit      area"]

            for specie in zone["species"]:
                name = _get(specie, "name", "''")
                name = fmt.format(name) if verbose else name
                values = [
                    _get(specie, "area_unit", 0),
                    _get(specie, "area", 0.0),
                ]
                tmp = _write_ffrecord(values, verbose)
                out += [f"{name} {tmp[0]}"]

    return out


@section("# Initial linear equilibrium Kd zones")
def _write_zlkd(parameters, verbose):
    """Write linear Kd zones."""
    out = []

    if "zones" not in parameters:
        return out

    kdtype = 0
    if "linear_kd" in parameters["zones"]:
        kdtype = len(parameters["zones"]["linear_kd"])

    if not kdtype:
        return out

    values = [kdtype]
    out += _write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["linear_kd"]):
        # Record 4
        values = [i + 1]
        out += _write_ffrecord(values)

        # Record 6
        values = [
            _get(zone, "name", 0),
            _get(zone, "solid_density", 0.0),
            _get(zone, "value", 0.0),
        ]
        out += _write_ffrecord(values)

    return out


@section("# Initial zones of cation exchange")
def _write_zexc(parameters, verbose):
    """Write cation exchange zones."""
    out = []

    if "zones" not in parameters:
        return out

    nxtype = 0
    if "cation_exchange" in parameters["zones"]:
        nxtype = len(parameters["zones"]["cation_exchange"])

    if not nxtype:
        return out

    values = [nxtype]
    out += _write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["cation_exchange"]):
        values = [i, *zone]
        out += _write_ffrecord(values)

    return out


def _write_ffrecord(values, verbose=False, int_fmt="{:4d}", float_fmt="{{:9f}}", str_fmt="{:20}"):
    return [(
        f"{' '.join(to_str(value, int_fmt if isinstance(value, int) else float_fmt if isinstance(value, float) else str_fmt) for value in values)}"
        if verbose
        else f"{' '.join(str(x) for x in values)}"
    )]
