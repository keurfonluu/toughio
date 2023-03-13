import os
from contextlib import contextmanager

import numpy as np

block_to_format = {
    "DIMEN": ",".join(8 * ["10d"]),
    "ROCKS": {
        1: "5s,5d,10.4e,10.4e,10.4e,10.4e,10.4e,10.4e,10.4e",
        2: "10.4e,10.4e,10.4e,10.3e,10.4e,10.4e,10.4e,10.4e,10.4e",  # Tortuosity can be <0 in TOUGHREACT
        # TOUGHREACT
        3: "5d,5s,10.3e,10.3e,10.3e",
        4: "5d,5s,14.6e,14.6e,14.6e,14.6e",
    },
    "RPCAP": "5d,5s,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e",
    "FLAC": {
        1: ",".join(16 * ["5d"]),
        2: "10d,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e",
        3: "5d,5s,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e",
    },
    "CHEMP": {
        1: "5d",
        2: "20s",
        3: ",".join(5 * ["10.3e"]),
    },
    "NCGAS": {1: "5d", 2: "10s"},
    "MULTI": ",".join(5 * ["5d"]),
    "SELEC": {1: ",".join(16 * ["5d"]), 2: ",".join(8 * ["10.3e"])},
    "SOLVR": "1d,2s,2s,3s,2s,10.4e,10.4e",
    "PARAM": {
        1: "2d,2d,4d,4d,4d,24S,10s,10.4e,10.4e",
        2: "10.4e,10.4e,10.1f,10.4e,5s,5s,10.4e,10.4e,10.4e",
        3: ",".join(8 * ["10.4e"]),
        4: "10.4e,10.4e,10s,10.4e,10.4e,10.4e",
        5: ",".join(4 * ["20.13e"]),
    },
    "INDOM": {0: ",".join(4 * ["20.13e"]), 5: "5s,5d"},  # 5d is for TMVOC
    "MOMOP": "50S",
    "TIMES": {1: "5d,5d,10.4e,10.4e", 2: ",".join(8 * ["10.4e"])},
    "HYSTE": ",".join(3 * ["5d"]),
    "FOFT": {5: "5s", 6: "6s", 7: "7s", 8: "8s", 9: "9s"},
    "COFT": {5: "10s", 6: "12s", 7: "14s", 8: "16s", 9: "18s"},
    "GOFT": {5: "5s", 6: "6s", 7: "7s", 8: "8s", 9: "9s"},
    "GENER": {
        0: ",".join(4 * ["14.7e"]),
        # Last integer is for KTAB value in TOUGHREACT
        5: "5s,5s,5d,5d,5d,5d,5s,4s,1s,10.3e,10.3e,10.3e,2d",
        6: "6s,5s,6d,4d,4d,5d,5s,4s,1s,10.3e,10.3e,10.3e,2d",
        7: "7s,5s,5d,4d,4d,5d,5s,4s,1s,10.3e,10.3e,10.3e,2d",
        8: "8s,5s,4d,4d,4d,5d,5s,4s,1s,10.3e,10.3e,10.3e,2d",
        9: "9s,5s,5d,3d,3d,5d,5s,4s,1s,10.3e,10.3e,10.3e,2d",
    },
    "DIFFU": ",".join(8 * ["10.3e"]),
    "OUTPU": {1: "20s", 2: "15s", 3: "20s,5d,5d"},
    "ELEME": {
        5: "5s,5d,5d,5s,10.4e,10.4e,10.4e,10f,10f,10f",
        6: "6s,5d,4d,5s,10.4e,10.4e,10.4e,10f,10f,10f",
        7: "7s,4d,4d,5s,10.4e,10.4e,10.4e,10f,10f,10f",
        8: "8s,4d,3d,5s,10.4e,10.4e,10.4e,10f,10f,10f",
        9: "9s,3d,3d,5s,10.4e,10.4e,10.4e,10f,10f,10f",
    },
    "COORD": ",".join(3 * ["20.13e"]),
    "CONNE": {
        5: "10s,5d,5d,5d,5d,10.4e,10.4e,10.4e,10.3e,10.3e",
        6: "12s,5d,4d,4d,5d,10.4e,10.4e,10.4e,10.3e,10.3e",
        7: "14s,5d,3d,3d,5d,10.4e,10.4e,10.4e,10.3e,10.3e",
        8: "16s,3d,3d,3d,5d,10.4e,10.4e,10.4e,10.3e,10.3e",
        9: "18s,3d,2d,2d,5d,10.4e,10.4e,10.4e,10.3e,10.3e",
    },
    "INCON": {
        0: ",".join(4 * ["20.13e"]),
        "default": {
            5: "5s,5d,5d,15.9e,10.3e,10.3e,10.3e,10.3e,10.3e",
            6: "6s,5d,4d,15.9e,10.3e,10.3e,10.3e,10.3e,10.3e",
            7: "7s,4d,4d,15.9e,10.3e,10.3e,10.3e,10.3e,10.3e",
            8: "8s,4d,3d,15.9e,10.3e,10.3e,10.3e,10.3e,10.3e",
            9: "9s,3d,3d,15.9e,10.3e,10.3e,10.3e,10.3e,10.3e",
        },
        "tmvoc": {
            5: "5s,5d,5d,15.9e,2d",
            6: "6s,5d,4d,15.9e,2d",
            7: "7s,4d,4d,15.9e,2d",
            8: "8s,4d,3d,15.9e,2d",
            9: "9s,3d,3d,15.9e,2d",
        },
        "toughreact": {
            5: "5s,5d,5d,15.9e,15.9e,15.9e,15.9e",
            6: "6s,5d,4d,15.9e,15.9e,15.9e,15.9e",
            7: "7s,4d,4d,15.9e,15.9e,15.9e,15.9e",
            8: "8s,4d,3d,15.9e,15.9e,15.9e,15.9e",
            9: "9s,3d,3d,15.9e,15.9e,15.9e,15.9e",
        },
    },
    "MESHM": {
        1: "5s",
        "XYZ": {
            1: "10.3e",
            2: "5s,5d,10.4e",
            3: ",".join(8 * ["10.4e"]),
        },
        "RZ2D": {
            1: "5s",
            "RADII": {
                1: "5d",
                2: ",".join(8 * ["10.3e"]),
            },
            "EQUID": "5d,5s,10.4e",
            "LOGAR": "5d,5s,10.4e,10.4e",
            "LAYER": {
                1: "5d",
                2: ",".join(8 * ["10.4e"]),
            },
        },
    },
    "REACT": "25S",
}


def str2format(fmt, ignore_types=None):
    """Convert a string to a list of formats."""
    ignore_types = ignore_types if ignore_types else ()

    token_to_format = {
        "s": "",
        "S": "",
        "d": "g",
        "f": "f",
        "e": "e",
    }

    base_fmt = "{{:{}}}"
    out = []
    for i, token in enumerate(fmt.split(",")):
        n = token[:-1]
        if i in ignore_types:
            out.append(base_fmt.format(n.split(".")[0]))
        elif token[-1].lower() == "s":
            out.append(base_fmt.format(f"{n}.{n}"))
        else:
            out.append(base_fmt.format(f">{n}{token_to_format[token[-1]]}"))

    return out


def get_label_length(label):
    """Get length of cell label."""
    label_length = 5
    while label_length < len(label) and label[label_length].isdigit():
        label_length += 1

    return max(min(label_length, 9), 5)


def register_format(
    fmt, ext_to_fmt, reader_map, writer_map, extensions, reader, writer
):
    """Register a new format."""
    for ext in extensions:
        ext_to_fmt[ext] = fmt

    if reader is not None:
        reader_map[fmt] = reader

    if writer is not None:
        writer_map[fmt] = writer


def filetype_from_filename(filename, ext_to_fmt):
    """Determine file type from its extension."""
    ext = os.path.splitext(filename)[1].lower()

    return ext_to_fmt[ext] if ext in ext_to_fmt else ""


@contextmanager
def open_file(path_or_buffer, mode):
    """Open file or buffer."""

    def is_buffer(obj, mode):
        return ("r" in mode and hasattr(obj, "read")) or (
            "w" in mode and hasattr(obj, "write")
        )

    if is_buffer(path_or_buffer, mode):
        yield path_or_buffer

    else:
        with open(path_or_buffer, mode) as f:
            yield f


def prune_values(data, value=None):
    """Remove values from dict or trailing values from list."""
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v != value}

    elif isinstance(data, (list, tuple, np.ndarray)):
        return [x for i, x in enumerate(data) if any(xx != value for xx in data[i:])]

    else:
        return data
