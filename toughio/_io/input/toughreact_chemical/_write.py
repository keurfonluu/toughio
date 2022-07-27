from ...._common import open_file
from .._common import getval, write_ffrecord
from ._helpers import section

__all__ = [
    "write",
]


def write(filename, parameters, verbose=True):
    """
    Write TOUGHREACT chemical input file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    parameters : dict
        Parameters to export.
    verbose : bool, optional, default True
        If `True`, add comments to describe content of file.

    """
    buffer = write_buffer(parameters, verbose)
    with open_file(filename, "w") as f:
        for record in buffer:
            f.write(record)


def write_buffer(parameters, verbose):
    """Write TOUGHREACT chemical input file."""
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
    out += _write_end_comments(parameters) if "end_comments" in parameters else []

    return "\n".join(out)


@section("# Title", f"#{'-' * 79}")
def _write_title(parameters):
    """Write title."""
    return [getval(parameters, "title", "")]


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
            getval(specie, "name", "''"),
            getval(specie, "transport", 0),
        ]

        if values[-1] == 2:
            values += [
                getval(specie, "mineral_name", "''"),
                getval(specie, "sorption_density", 0.0),
                getval(specie, "adsorption_id", 0),
            ]

            if values[-1] == 1:
                values += [getval(specie, "capacitance", 0.0)]

        out += write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

    return out


@section("# Aqueous kinetics")
def _write_akin(parameters, verbose):
    """Write aqueous kinetics."""
    out = []

    if not ("aqueous_kinetics" in parameters and parameters["aqueous_kinetics"]):
        return out

    # Record 2
    out += [f"{len(parameters['aqueous_kinetics'])}"]

    for i, kinetic in enumerate(parameters["aqueous_kinetics"]):
        # Record 3
        out += [f"{i + 1}"]

        # Record 4
        n = len(kinetic["species"])
        values = [n]
        if n:
            for specie in kinetic["species"]:
                values += [
                    getval(specie, "stoichiometric_coeff", 1.0),
                    getval(specie, "name", "''"),
                ]

        if "reaction_affinity" in kinetic:
            values += [
                getval(kinetic, ("reaction_affinity", "id"), 0),
                getval(kinetic, ("reaction_affinity", "cf"), 0.0),
                getval(kinetic, ("reaction_affinity", "logK"), 0.0),
            ]

        out += write_ffrecord(values)

        # Record 5
        values = [
            getval(kinetic, "id", 0),
            getval(kinetic, "n_mechanism", 0),
        ]
        tmp = write_ffrecord(values)

        # Record 6
        rate = getval(kinetic, "rate", 0.0)
        rate = rate if not isinstance(rate, dict) else -1.0
        tmp += [f"{rate}"]

        # Record 6.1
        if rate == -1.0:
            values = [
                getval(kinetic, ("rate", "k25"), 0.0),
                getval(kinetic, ("rate", "Ea"), 0.0),
            ]
            tmp += write_ffrecord(values)

        # Record 7
        ncp_rx1 = len(kinetic["product"])
        values = [ncp_rx1]
        if ncp_rx1:
            for specie in kinetic["product"]:
                values += [
                    getval(specie, "specie", "''"),
                    getval(specie, "flag", 0),
                    getval(specie, "power", 0.0),
                ]
        tmp += write_ffrecord(values)

        # Record 8
        ncp_rx2 = len(kinetic["monod"])
        values = [ncp_rx2]
        if ncp_rx2:
            for specie in kinetic["monod"]:
                values += [
                    getval(specie, "specie", "''"),
                    getval(specie, "flag", 0),
                    getval(specie, "half_saturation", 0.0),
                ]
        tmp += write_ffrecord(values)

        # Record 9
        ncp_rx3 = len(kinetic["inhibition"])
        values = [ncp_rx3]
        if ncp_rx3:
            for specie in kinetic["inhibition"]:
                values += [
                    getval(specie, "specie", "''"),
                    getval(specie, "flag", 0),
                    getval(specie, "constant", 0.0),
                ]
        tmp += write_ffrecord(values)

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
    """Write minerals."""
    out = []

    if not ("minerals" in parameters and parameters["minerals"]):
        return out

    if verbose:
        item = max(parameters["minerals"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for mineral in parameters["minerals"]:
        # Record 2
        ikin = getval(mineral, "type", 0)
        idispre = getval(mineral, "kinetic_constraint", 0)
        values = [
            getval(mineral, "name", "''"),
            ikin,
            idispre,
            getval(mineral, "solid_solution", 0),
            getval(mineral, "precipitation_dry", 0),
        ]
        out += write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

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

                idep = getval(mineral, (key, "rate_ph_dependence"), 0)
                values = [
                    getval(mineral, (key, "k25"), 0.0),
                    idep,
                    getval(mineral, (key, "eta"), 0.0),
                    getval(mineral, (key, "theta"), 0.0),
                    getval(mineral, (key, "activation_energy"), 0.0),
                    getval(mineral, (key, "a"), 0.0),
                    getval(mineral, (key, "b"), 0.0),
                    getval(mineral, (key, "c"), 0.0),
                ]

                # Record 2.2
                if key == "precipitation":
                    values += [
                        getval(mineral, (key, "volume_fraction_ini"), 0.0),
                        getval(mineral, (key, "id"), 0),
                    ]

                out += write_ffrecord(values)

                # Record 2.1.1
                if idep == 1:
                    values = [
                        getval(mineral, (key, "ph1"), 0.0),
                        getval(mineral, (key, "slope1"), 0.0),
                        getval(mineral, (key, "ph2"), 0.0),
                        getval(mineral, (key, "slope2"), 0.0),
                    ]
                    out += write_ffrecord(values)

                # Record 2.1.2
                elif idep == 2:
                    ndis = (
                        len(mineral[key]["extra_mechanisms"])
                        if "extra_mechanisms" in mineral[key]
                        else 0
                    )
                    values = [ndis]
                    out += write_ffrecord(values)

                    # Record 2.1.2.1
                    if ndis:
                        for mechanism in mineral[key]["extra_mechanisms"]:
                            values = [
                                getval(mechanism, "ki", 0.0),
                                getval(mechanism, "activation_energy", 0.0),
                            ]

                            nspds = len(getval(mechanism, "species", []))
                            values += [nspds]
                            if nspds:
                                for specie in mechanism["species"]:
                                    values += [
                                        getval(specie, "name", "''"),
                                        getval(specie, "power", 0.0),
                                    ]
                            out += write_ffrecord(values)

        # Record 2.3
        if idispre != 1:
            values = [
                getval(mineral, "gap", 0.0),
                getval(mineral, "temp1", 0.0),
                getval(mineral, "temp2", 0.0),
            ]
            out += write_ffrecord(values)

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
            getval(specie, "name", "''"),
            getval(specie, "fugacity", 0),
        ]
        out += write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

    return out


@section("# Surface complexes")
def _write_surx(parameters):
    """Write surface complexes."""
    out = []

    if not ("surface_complexes" in parameters and parameters["surface_complexes"]):
        return out

    for complex_ in parameters["surface_complexes"]:
        out += [f"{complex_:<20}"]

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
            getval(specie, "name", "''"),
            getval(specie, "decay_constant", 0.0),
            getval(specie, "a", 0.0),
            getval(specie, "b", 0.0),
        ]
        out += write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

    return out


@section("# Exchangeable cations")
def _write_exch(parameters, verbose):
    """Write exchanges species."""
    out = []

    if not ("exchanged_species" in parameters and parameters["exchanged_species"]):
        return out

    # Record 2
    nxsites = len(getval(parameters["exchanged_species"][0], "site_coeffs", []))
    values = [
        nxsites,
        getval(parameters, "exchange_sites_id", 0),
    ]
    out += write_ffrecord(values, verbose, int_fmt="{:<4d}")

    # Record 3
    if verbose:
        item = max(parameters["exchanged_species"], key=lambda x: len(x["name"]))
        n = min(len(item["name"]), 20)
        fmt = f"{{:{n}}}"

        out += [f"# {' ' * (n - 2)} ref. type    coeff."]

    for specie in parameters["exchanged_species"]:
        values = [
            getval(specie, "name", "''"),
            int(getval(specie, "reference", False)),
            getval(specie, "type", 1),
        ]
        values += [*getval(specie, "site_coeffs", [])]
        out += write_ffrecord(values, verbose, str_fmt=fmt if verbose else None)

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
    out += write_ffrecord(values, verbose, int_fmt="{:<4d}")

    for k, v in nwtypes.items():
        if not v:
            continue

        for i, zone in enumerate(parameters["zones"][k]):
            # Record 4
            if verbose:
                out += ["#         T(C)    P(bar)"]

                if "rock" in zone:
                    out[-1] = f"{out[-1]}      Rock"

            values = [
                i + 1 if "rock" not in zone else -1,
                getval(zone, "temperature", 0.0),
                getval(zone, "pressure", 0.0),
            ]
            values += [getval(zone, "rock", "''")[:5]] if "rock" in zone else []
            out += write_ffrecord(values, verbose, int_fmt="{:<4d}", str_fmt="{:>9}")

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

                    out += [
                        f"# {' ' * (n - 2)} icon     guess      ctot {fmt2.format('constraint')}  log(Q/K)"
                    ]

                for specie in zone["species"]:
                    name = getval(specie, "name", "''")
                    name = fmt1.format(name) if verbose else name
                    nameq = "*" if "nameq" not in specie else specie["nameq"]
                    values = [
                        getval(specie, "flag", 0),
                        getval(specie, "guess", 0.0),
                        getval(specie, "ctot", 0.0),
                        nameq,  # nameq is optional
                        getval(specie, "log_fugacity", 0.0),
                    ]
                    tmp = write_ffrecord(
                        values, verbose, str_fmt=fmt2 if verbose else None
                    )
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
    out += write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["minerals"]):
        # Record 4
        values = [i + 1] if "rock" not in zone else [-(i + 1), f"'{zone['rock'][:5]}'"]
        out += write_ffrecord(values)

        # Record 6
        if "species" in zone and zone["species"]:
            if verbose:
                item = max(zone["species"], key=lambda x: len(x["name"]))
                fmt = f"{{:{max(len(item['name']), 10)}}}"

            for mineral in zone["species"]:
                name = getval(mineral, "name", "''")
                name = fmt.format(name) if verbose else name
                flag = getval(mineral, "flag", 0)
                values = [
                    getval(mineral, "volume_fraction_ini", 0.0),
                    flag,
                ]
                tmp = write_ffrecord(values, verbose)
                out += [f"{name} {tmp[0]}"]

                # Record 6.1
                if flag == 1:
                    area_unit = getval(mineral, "area_unit", 0)
                    values = [
                        getval(mineral, "radius", 0.0),
                        getval(mineral, "area_ini", 0.0),
                        area_unit,
                    ]
                    out += write_ffrecord(values, verbose)
                    out[-1] = out[-1].lstrip()

                    # TODO: investigate what is the next record when IMFLG2 < 0
                    # This record is not documented in the user guide (p. 65)
                    if area_unit < 0:
                        values = getval(mineral, "unknown", [])
                        out += write_ffrecord(values, verbose)

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
    out += write_ffrecord(values, verbose, int_fmt="{:<4d}")

    for k, v in ngtypes.items():
        if not v:
            continue

        for i, zone in enumerate(parameters["zones"][k]):
            # Record 4
            values = [i + 1]
            out += write_ffrecord(values, verbose, int_fmt="{:<4d}")

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
                name = getval(specie, "name", "''")
                name = fmt.format(name) if verbose else name
                values = [
                    (
                        getval(specie, "partial_pressure", 0.0)
                        if k == "initial_gases"
                        else getval(specie, "mole_fraction", 0.0)
                    )
                ]
                tmp = write_ffrecord(values, verbose)
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
    out += write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["permeability_porosity"]):
        # Record 4
        values = [i + 1]
        out += write_ffrecord(values)

        # Record 6
        if verbose:
            out += ["#        a-par     b-par"]

        values = [
            getval(zone, "id", 0),
            getval(zone, "a", 0.0),
            getval(zone, "b", 0.0),
        ]
        out += write_ffrecord(values, verbose, int_fmt="{:<4d}")

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
    out += write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["adsorption"]):
        # Record 5
        values = [
            i + 1,
            getval(zone, "flag", 0),
        ]
        out += write_ffrecord(values)

        # Record 6
        if "species" in zone and zone["species"]:
            if verbose:
                item = max(zone["species"], key=lambda x: len(x["name"]))
                n = max(len(item["name"]), 10)
                fmt = f"{{:{n}}}"

                out += [f"# {' ' * (n - 2)} unit      area"]

            for specie in zone["species"]:
                name = getval(specie, "name", "''")
                name = fmt.format(name) if verbose else name
                values = [
                    getval(specie, "area_unit", 0),
                    getval(specie, "area", 0.0),
                ]
                tmp = write_ffrecord(values, verbose)
                out += [f"{name} {tmp[0]}"]

        # Record 7
        out += ["*"]

    return out[:-1]


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
    out += write_ffrecord(values)

    for i, zone in enumerate(parameters["zones"]["linear_kd"]):
        # Record 4
        values = [i + 1]
        out += write_ffrecord(values)

        # Record 6
        if verbose:
            item = max(zone, key=lambda x: len(x["name"]))
            n = min(len(item["name"]), 10)
            fmt = f"{{:{n}}}"

            out += [f"# {' ' * n} density        Kd"]

        for specie in zone:
            name = getval(specie, "name", "''")
            name = fmt.format(name) if verbose else name
            values = [
                getval(specie, "solid_density", 0.0),
                getval(specie, "value", 0.0),
            ]
            tmp = write_ffrecord(values, verbose)
            out += [f"{name} {tmp[0]}"]

        # Record 7
        out += ["*"]

    return out[:-1]


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
    out += write_ffrecord(values)

    if verbose:
        out += ["#     capacity"]

    for i, zone in enumerate(parameters["zones"]["cation_exchange"]):
        values = [i + 1, *zone]
        out += write_ffrecord(values, verbose, int_fmt="{:<4d}")

    return out


def _write_end_comments(parameters):
    """Write end comments."""
    end_comments = getval(parameters, "end_comments", "")

    return [end_comments] if isinstance(end_comments, str) else end_comments
