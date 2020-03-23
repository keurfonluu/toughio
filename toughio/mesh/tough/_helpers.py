__all__ = [
    "block",
    "_write_eleme",
    "_write_conne",
]


def block(keyword):
    """Decorate block writing functions."""

    def decorator(func):
        from functools import wraps

        header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"

        @wraps(func)
        def wrapper(f, *args):
            f.write("{}{}\n".format(keyword, header))
            func(f, *args)
            f.write("\n")

        return wrapper

    return decorator


def _write_eleme(labels, materials, volumes, nodes, material_name=None):
    """Return a generator that iterates over the records of block ELEME."""
    fmt = "{:5.5}{:>5}{:>5}{:>5}{:10.4e}{:>10}{:>10}{:10.3e}{:10.3e}{:10.3e}\n"

    iterables = zip(labels, materials, volumes, nodes)
    for label, material, volume, node in iterables:
        mat = (
            material_name[material]
            if material_name and material in material_name.keys()
            else material
        )
        record = fmt.format(
            label,  # ID
            "",  # NSEQ
            "",  # NADD
            mat,  # MAT
            volume,  # VOLX
            "",  # AHTX
            "",  # PMX
            node[0],  # X
            node[1],  # Y
            node[2],  # Z
        )
        yield record


def _write_conne(clabels, isot, d1, d2, areas, angles):
    """Return a generator that iterates over the records of block CONNE."""
    fmt = "{:10.10}{:>5}{:>5}{:>5}{:>5g}{:10.4e}{:10.4e}{:10.4e}{:10.3e}\n"

    iterables = zip(clabels, isot, d1, d2, areas, angles)
    for label, isot, d1, d2, area, angle in iterables:
        record = fmt.format(
            label,  # ID1-ID2
            "",  # NSEQ
            "",  # NAD1
            "",  # NAD2
            isot,  # ISOT
            d1,  # D1
            d2,  # D2
            area,  # AREAX
            angle,  # BETAX
        )
        yield record


def _write_incon(labels, values, porosity=None, userx=None):
    """Return a generator that iterates over the records of block INCON."""
    porosity = porosity if porosity is not None else [None] * len(labels)
    userx = userx if userx is not None else [None] * len(labels)

    iterables = zip(labels, values, porosity, userx)
    for label, value, phi, usrx in iterables:
        cond1 = any(v > -1.0e-9 for v in value)
        cond2 = phi is not None
        cond3 = usrx is not None
        if cond1 or cond2 or cond3:
            record = "{:5.5}{:10}".format(label, "")

            record += "{:15.9e}".format(phi) if phi is not None else "{:15}".format("")

            if usrx is not None:
                fmt = "{:10.3e}" * len(usrx)
                record += fmt.format(*usrx)
            record += "\n"

            for v in value:
                record += "{:20.13e}".format(v) if v > -1.0e9 else "{:20}".format("")
            record += "\n"

            yield record
        else:
            continue
