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
    ntrx = int(line.split()[0])
    akin["aqueous_kinetics"] = [{} for _ in range(ntrx)]

    # Loop n times
    for _ in range(ntrx):
        # Record 3
        line = _nextline(f).strip()
        irx = int(line.split()[0])

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
                "flag": data[3 * i + 2],
                "power": data[3 * i + 3],
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
                "flag": data[3 * i + 2],
                "half_saturation": data[3 * i + 3],
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
                "flag": data[3 * i + 2],
                "constant": data[3 * i + 3],
            }
            for i in range(ncp_rx3)
        ]
        
        akin["aqueous_kinetics"][irx - 1].update(tmp)

    return akin


def _nextline(f, **kwargs):
    line = f.next(**kwargs)
    line = line.replace("'", "")  # Remove quotes
    
    if "!" in line:
        line = line[:line.index("!")]

    return line
