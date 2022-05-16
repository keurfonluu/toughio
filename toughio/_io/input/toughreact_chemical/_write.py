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

    return "\n".join(out)


@section("# Title", f"#{'-' * 79}")
def _write_title(parameters):
    """Write title."""
    return [f"{parameters['title']}"]


@section("# Primary aqueous species")
def _write_prim(parameters, verbose):
    """Write primary species."""
    out = []

    if "primary_species" not in parameters:
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

        out += _write_ffrecord(values, verbose, str_fmt=fmt)

    return out


@section("# Aqueous kinetics")
def _write_akin(parameters, verbose):
    out = []

    if "aqueous_kinetics" not in parameters:
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

                if "reaction_affinity" in specie:
                    values += [
                        _get(specie, ("reaction_affinity", "id"), 0),
                        _get(specie, ("reaction_affinity", "cf"), 0.0),
                        _get(specie, ("reaction_affinity", "logK"), 0.0),
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

    if "aqueous_species" not in parameters:
        return out

    for specie in parameters["aqueous_species"]:
        out += [f"{specie:<20}"]

    return out


@section("# Minerals")
def _write_miner(parameters, verbose):
    out = []

    if "minerals" not in parameters:
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
        out += _write_ffrecord(values, verbose, str_fmt=fmt)

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
                    values += [
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

    if "gaseous_species" not in parameters:
        return out

    if verbose:
        item = max(parameters["gaseous_species"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for specie in parameters["gaseous_species"]:
        values = [
            _get(specie, "name", "''"),
            _get(specie, "fugacity", 0),
        ]
        out += _write_ffrecord(values, verbose, str_fmt=fmt)

    return out


@section("# Surface complexes")
def _write_surx(parameters):
    """Write surface complexes."""
    out = []

    if "surface_complexes" not in parameters:
        return out

    for complex in parameters["surface_complexes"]:
        out += [f"{complex:<20}"]

    return out


@section("# Species with Kd and decay")
def _write_kdde(parameters, verbose):
    """Write Kd and decay."""
    out = []

    if "kd_decay" not in parameters:
        return out

    if verbose:
        item = max(parameters["kd_decay"], key=lambda x: len(x["name"]))
        fmt = f"{{:{min(len(item['name']), 20)}}}"

    for specie in parameters["gaseous_species"]:
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

    if "exchanged_species" not in parameters:
        return out

    # Record 2
    nxsites = len(parameters["exchanged_species"])
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
        values += _get(specie, "site_coeffs", [])
        out += _write_ffrecord(values, verbose, str_fmt=fmt)

    return out


def _write_ffrecord(values, verbose=False, int_fmt="{:4d}", float_fmt="{{:9f}}", str_fmt="{:20}"):
    return [(
        f"{' '.join(to_str(value, int_fmt if isinstance(value, int) else float_fmt if isinstance(value, float) else str_fmt) for value in values)}"
        if verbose
        else f"{' '.join(str(x) for x in values)}"
    )]
