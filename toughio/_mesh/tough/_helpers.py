from ..._common import block_to_format, str2format
from ..._io.input.tough._helpers import write_record


def block(keyword):
    """Decorate block writing functions."""

    def decorator(func):
        from functools import wraps

        header = "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"

        @wraps(func)
        def wrapper(f, *args):
            f.write(f"{keyword}{header}\n")
            func(f, *args)
            f.write("\n")

        return wrapper

    return decorator


def _write_eleme(labels, materials, volumes, nodes, material_name=None):
    """Return a generator that iterates over the records of block ELEME."""
    label_length = len(labels[0])
    fmt = block_to_format["ELEME"][label_length]
    fmt = str2format(fmt)

    iterables = zip(labels, materials, volumes, nodes)
    for label, material, volume, node in iterables:
        mat = (
            material_name[material]
            if material_name and material in material_name
            else material
        )
        mat = mat if isinstance(mat, str) else f"{str(mat):>5}"
        record = write_record(
            [
                label,  # ID
                None,  # NSEQ
                None,  # NADD
                mat,  # MAT
                volume,  # VOLX
                None,  # AHTX
                None,  # PMX
                node[0],  # X
                node[1],  # Y
                node[2],  # Z
            ],
            fmt=fmt,
        )
        yield record[0]


def _write_coord(nodes):
    """Return a generator that iterates over the records of block COORD."""
    fmt = "{:20.13e}{:20.13e}{:20.13e}\n"

    for node in nodes:
        record = fmt.format(*node)
        yield record


def _write_conne(clabels, isot, d1, d2, areas, angles):
    """Return a generator that iterates over the records of block CONNE."""
    label_length = len(clabels[0][0])
    fmt = block_to_format["CONNE"][label_length]
    fmt = str2format(fmt)

    iterables = zip(clabels, isot, d1, d2, areas, angles)
    for label, isot, d1, d2, area, angle in iterables:
        record = write_record(
            [
                "".join(label),  # ID1-ID2
                None,  # NSEQ
                None,  # NAD1
                None,  # NAD2
                isot,  # ISOT
                d1,  # D1
                d2,  # D2
                area,  # AREAX
                angle,  # BETAX
                None,  # SIGX
            ],
            fmt=fmt,
        )
        yield record[0]


def _write_incon(
    labels, values, porosity=None, userx=None, phase_composition=None, eos=None
):
    """Return a generator that iterates over the records of block INCON."""
    porosity = porosity if porosity is not None else [None] * len(labels)
    userx = userx if userx is not None else [None] * len(labels)
    phase_composition = (
        phase_composition if phase_composition is not None else [None] * len(labels)
    )
    label_length = len(labels[0])
    fmt = block_to_format["INCON"]

    iterables = zip(labels, values, porosity, userx, phase_composition)
    for label, value, phi, usrx, indicat0 in iterables:
        cond1 = any(v > -1.0e-9 for v in value)
        cond2 = phi is not None
        cond3 = usrx is not None
        if cond1 or cond2 or cond3:
            # Record 1
            values = [label, "", ""]
            ignore_types = [1, 2]

            if phi is not None:
                values.append(phi)
            else:
                values.append("")
                ignore_types.append(3)

            if eos == "tmvoc":
                if indicat0 is not None:
                    values.append(indicat0)
                else:
                    values.append("")
                    ignore_types.append(4)

            else:
                if usrx is not None:
                    values += list(usrx)
                else:
                    values += 3 * [""]
                    ignore_types += [4, 5, 6]

            fmt1 = str2format(
                fmt[eos][label_length] if eos in fmt else fmt["default"][label_length],
                ignore_types=ignore_types,
            )
            fmt1 = f"{''.join(fmt1[: len(values)])}\n"
            record = fmt1.format(*values)

            # Record 2
            n = min(4, len(value))
            values = []
            ignore_types = []
            for i, v in enumerate(value[:n]):
                if v > -1.0e9:
                    values.append(v)
                else:
                    values.append("")
                    ignore_types.append(i)

            fmt2 = str2format(fmt[0], ignore_types=ignore_types)
            fmt2 = f"{''.join(fmt2[: len(values)])}\n"
            record += fmt2.format(*values)

            # Record 3 (EOS7R)
            if len(value) > 4:
                values = []
                ignore_types = []
                for i, v in enumerate(value[n:]):
                    if v > -1.0e9:
                        values.append(v)
                    else:
                        values.append("")
                        ignore_types.append(i)

                fmt2 = str2format(fmt[0], ignore_types=ignore_types)
                fmt2 = f"{''.join(fmt2[: len(values)])}\n"
                record += fmt2.format(*values)

            yield record
        else:
            continue
