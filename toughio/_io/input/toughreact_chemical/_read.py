from ...._common import open_file
from ...._exceptions import ReadError
from ...._helpers import FileIterator
from ..._common import read_record, prune_nones_list, to_float

__all__ = [
    "read",
]


def read(filename):
    """
    Read TOUGHREACT chemical input file.

    Parameters
    ----------
    filename : str
        Input file name.

    """
    with open_file(filename, "r") as f:
        out = read_buffer(f)

    return out


def read_buffer(f):
    """Read TOUGHREACT chemical input file."""
    parameters = {}
    fiter = FileIterator(f)

    try:
        parameters.update(_read_title(fiter))
        parameters.update(_read_prim(fiter))
        parameters.update(_read_akin(fiter))
        parameters.update(_read_aque(fiter))
        parameters.update(_read_miner(fiter))
        parameters.update(_read_gas(fiter))
        parameters.update(_read_surx(fiter))
        parameters.update(_read_kdde(fiter))
        parameters.update(_read_exch(fiter))

    except:
        raise ReadError("failed to parse line {}.".format(fiter.count))

    return parameters


def _read_title(f):
    """Read title."""
    line = f.next(skip_empty=True, comments="#").strip()
    
    return {"title": line}


def _read_prim(f):
    """Read primary species."""
    prim = {"primary_species": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    # Loop until reading character *
    while not line.startswith("*"):
        data = line.split()
        if len(data) < 2:
            raise ReadError()

        tmp = {
            "name": data[0],
            "transport": int(data[1])
        }
        if len(data) >= 3:
            tmp["mineral_name"] = data[2]
        if len(data) >= 4:
            tmp["sorption_density"] = to_float(data[3])
        if len(data) >= 5:
            tmp["adsorption_id"] = int(data[4])
        if len(data) >= 6:
            tmp["capacitance"] = to_float(data[5])
        prim["primary_species"].append(tmp)

        line = _nextline(f).strip()

    return prim


def _read_akin(f):
    """Read aqueous kinetics."""
    akin = {"aqueous_kinetics": None}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    if line.startswith("*"):
        return {}

    # Record 2
    ntrx = int(line.strip())
    akin["aqueous_kinetics"] = [{} for _ in range(ntrx)]

    # Loop ntrx times
    for _ in range(ntrx):
        # Record 3
        line = _nextline(f).strip()
        irx = int(line.strip())

        # Record 4
        line = _nextline(f).strip()
        data = line.split()
        ncp = int(data[0])
        if len(data) < 2 * ncp + 1:
            raise ReadError()
        
        names = data[2:2 * ncp + 2:2]
        coeffs = data[1:2 * ncp + 1:2]
        tmp = {
            "aqueous_species": [
                {
                    "name": name,
                    "stoichiometric_coeff": coeff,
                }
                for name, coeff in zip(names, coeffs)
            ]
        }

        if len(data) > 2 * ncp + 1:
            tmp["reaction_affinity"] = {
                "id": int(data[2 * ncp + 1]),
                "cf": int(data[2 * ncp + 2]),
                "logK": int(data[2 * ncp + 3]),
            }

        # Record 5
        line = _nextline(f).strip()
        data = line.split()
        tmp["kinetic_model_id"] = int(data[0])
        tmp["n_mechanism"] = int(data[1])

        # Record 6
        line = _nextline(f).strip()
        data = to_float(line.split()[0])
        tmp["rate"] = {"constant": data}

        # Record 6.1
        if tmp["rate"]["constant"] == -1.0:
            line = _nextline(f).strip()
            data = line.split()
            tmp["rate"]["k25"] = to_float(data[0])
            tmp["rate"]["Ea"] = to_float(data[1])

        # Record 7
        line = _nextline(f).strip()
        data = line.split()
        ncp_rx1 = int(data[0])
        if len(data) < 3 * ncp_rx1 + 1:
            raise ReadError()

        tmp["product"] = [
            {
                "specie": data[3 * i + 1],
                "flag": int(data[3 * i + 2]),
                "power": to_float(data[3 * i + 3]),
            }
            for i in range(ncp_rx1)
        ]

        # Record 8
        line = _nextline(f).strip()
        data = line.split()
        ncp_rx2 = int(data[0])
        if len(data) < 3 * ncp_rx2 + 1:
            raise ReadError()

        tmp["monod"] = [
            {
                "specie": data[3 * i + 1],
                "flag": int(data[3 * i + 2]),
                "half_saturation": to_float(data[3 * i + 3]),
            }
            for i in range(ncp_rx2)
        ]

        # Record 9
        line = _nextline(f).strip()
        data = line.split()
        ncp_rx3 = int(data[0])
        if len(data) < 3 * ncp_rx3 + 1:
            raise ReadError()

        tmp["inhibition"] = [
            {
                "specie": data[3 * i + 1],
                "flag": int(data[3 * i + 2]),
                "constant": to_float(data[3 * i + 3]),
            }
            for i in range(ncp_rx3)
        ]
        
        akin["aqueous_kinetics"][irx - 1].update(tmp)

    return akin


def _read_aque(f):
    """Read aqueous species."""
    aque = {"aqueous_species": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    # Loop until reading character *
    while not line.startswith("*"):
        data = line.strip()
        aque["aqueous_species"].append(data)

        line = _nextline(f)

    return aque


def _read_miner(f):
    """Read minerals."""
    miner = {"minerals": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")
    
    # Loop until reading character *
    while not line.startswith("*"):
        # Record 2
        data = _nextsplitline(line, 5)

        tmp = {
            "name": data[0],
            "type": int(data[1]),
            "kinetic_constraint": int(data[2]),
            "solid_solution": int(data[3]),
            "precipitation_dry": int(data[4]),
        }

        # Records 2.1 and 2.2
        # The 8 first entries of record 2.2 are common with record 2.1
        if tmp["type"] == 1:
            n = 2 if tmp["kinetic_constraint"] == 3 else 1
            for ir in range(n):
                if tmp["kinetic_constraint"] == 1:
                    key = "dissolution"

                elif tmp["kinetic_constraint"] == 2:
                    key = "precipitation"

                elif tmp["kinetic_constraint"] == 3:
                    key = "dissolution" if ir == 0 else "precipitation"

                data = (
                    _nextsplitline(f, 8)
                    if key == "dissolution"
                    else _nextsplitline(f, 10)
                )

                tmp[key] = {}
                tmp[key]["k25"] = to_float(data[0])
                tmp[key]["rate_ph_dependence"] = int(data[1])
                tmp[key]["eta"] = to_float(data[2])
                tmp[key]["theta"] = to_float(data[3])
                tmp[key]["activation_energy"] = to_float(data[4])
                tmp[key]["a"] = to_float(data[5])
                tmp[key]["b"] = to_float(data[6])
                tmp[key]["c"] = to_float(data[7])

                if key == "precipitation":
                    tmp[key]["volume_fraction_ini"] = to_float(data[8])
                    tmp[key]["id"] = int(data[9])

                if tmp[key]["rate_ph_dependence"] == 1:
                    data = _nextsplitline(f, 4)

                    tmp[key]["ph1"] = to_float(data[0])
                    tmp[key]["slope1"] = to_float(data[1])
                    tmp[key]["ph2"] = to_float(data[2])
                    tmp[key]["slope2"] = to_float(data[3])

                elif tmp[key]["rate_ph_dependence"] == 2:
                    tmp[key]["extra_mechanisms"] = []

                    line = _nextline(f).strip()
                    ndis = int(line.strip())

                    for _ in range(ndis):
                        line = _nextline(f).strip()
                        data = line.split()
                        nspds = int(data[2])
                        if len(data) < 2 * nspds + 3:
                            raise ReadError()

                        tmp[key]["extra_mechanisms"].append(
                            {
                                "ki": to_float(data[0]),
                                "activation_energy": to_float(data[1]),
                                "mechanism": [
                                    {
                                        "specie": data[2 * i + 3],
                                        "power": to_float(data[2 * i + 4]),
                                    }
                                    for i in range(nspds)
                                ]
                            }
                        )

        # Record 3
        data = _nextsplitline(f, 3)

        tmp["gap"] = to_float(data[0])
        tmp["temp1"] = to_float(data[1])
        tmp["temp2"] = to_float(data[2])

        miner["minerals"].append(tmp)
        line = _nextline(f)

    return miner


def _read_gas(f):
    """Read gaseous species."""
    gas = {"gaseous_species": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    # Loop until reading character *
    while not line.startswith("*"):
        data = line.split()
        if len(data) < 2:
            raise ReadError()

        tmp = {
            "name": data[0],
            "fugacity": int(data[1]),
        }
        gas["gaseous_species"].append(tmp)

        line = _nextline(f).strip()

    return gas


def _read_surx(f):
    """Read surface complexe."""
    surx = {"surface_complexes": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    # Loop until reading character *
    while not line.startswith("*"):
        data = line.strip()
        surx["surface_complexes"].append(data)

        line = _nextline(f)

    return surx


def _read_kdde(f):
    """Read Kd and decay."""
    kdde = {"kd_decay": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    # Loop until reading character *
    while not line.startswith("*"):
        data = line.split()
        if len(data) < 4:
            raise ReadError()

        tmp = {
            "name": data[0],
            "decay_constant": to_float(data[1]),
            "a": to_float(data[2]),
            "b": to_float(data[3]),
        }
        kdde["kd_decay"].append(tmp)

        line = _nextline(f).strip()

    return kdde


def _read_exch(f):
    """Read exchanged species."""
    exch = {"exchanged_species": []}

    # Find next non skip record
    line = _nextline(f, skip_empty=True, comments="#")

    if line.startswith("*"):
        return {}

    # Record 2
    data = line.split()
    if len(data) < 2:
        raise ReadError()

    nxsites = int(data[0])
    exch["exchange_sites_id"] = int(data[1])

    # Record 4
    line = _nextline(f, skip_empty=True, comments="#")

    # Loop until reading character *
    while not line.startswith("*"):
        data = line.split()
        if len(data) < nxsites + 3:
            raise ReadError()

        tmp = {
            "name": data[0],
            "reference": bool(data[1]),
            "type": int(data[2]),
            "site_coeffs": [to_float(x) for x in data[3:]],
        }
        exch["exchanged_species"].append(tmp)

        line = _nextline(f).strip()

    return exch


def _nextline(f, **kwargs):
    line = f.next(**kwargs)
    line = line.replace("'", "")  # Remove quotes
    
    # Remove Fortran comments
    if "!" in line:
        line = line[:line.index("!")]

    return line


def _nextsplitline(f_or_line, n=0, **kwargs):
    if not isinstance(f_or_line, str):
        line = _nextline(f_or_line, **kwargs).strip()
    else:
        line = f_or_line

    data = line.split()
    if len(data) < n:
        raise ReadError(f"expected at least {n} entries, got {len(data)}.")

    return data
