import os

__all__ = [
    "register_format",
    "filetype_from_filename",
]


block_to_format_dict = {
    "ROCKS": {
        1: "5s,5d,10.4e,10.4e,10.4e,10.4e,10.4e,10.4e,10.4e",
        2: ",".join(7 * ["10.4e"]),
    },
    "RPCAP": "5d,5s,10e,10e,10e,10e,10e,10e,10e",
    "FLAC": {
        1: ",".join(16 * ["5d"]),
        2: "10d,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e",
        3: "5d,5s,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e,10.3e",
    },
    "SELEC": {
        1: ",".join(16 * ["5d"]),
        2: ",".join(8 * ["10.3e"]),
    },
    "SOLVR": "1d,2s,2s,3s,2s,10.4e,10.4e",
    "PARAM": {
        1: "2d,2d,4d,4d,4d,24S,10s,10.4e,10.4e",
        2: "10.4e,10.4e,10.1f,10.4e,10s,10.4e,10.4e,10.4e",
        3: "10.4e,10.4e,10.4e,10.4e,10.4e,10.4e,10.4e,10.4e",
        4: "10.4e,10.4e,10s,10.4e,10.4e,10.4e",
        5: ",".join(4 * ["20.13e"]),
    },
    "INDOM": ",".join(4 * ["20.13e"]),
    "MOMOP": "40S",
    "TIMES": {
        1: "5d,5d,10.4e,10.4e",
        2: ",".join(8 * ["10.4e"]),
    },
    "GENER": {
        0: ",".join(4 * ["14.7e"]),
        5: "5s,5s,5d,5d,5d,5d,5s,4s,1s,10.3e,10.3e,10.3e",
    },
    "DIFFU": ",".join(8 * ["10.3e"]),
    "OUTPU": "20s,5d,5d",
    "ELEME": {
        5: "5s,5d,5d,5s,10.4e,10.4e,10.4e,10.3e,10.3e,10.3e",
    },
    "CONNE": {
        5: "10s,5d,5d,5d,5d,10.4e,10.4e,10.4e,10.4e,10.3e",
    },
    "INCON": {
        0: ",".join(4 * ["20.13e"]),
        5: "5s,5d,5d,15.9e,10.3e,10.3e,10.3e,10.3e,10.3e",
    },
}


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

    return ext_to_fmt[ext] if ext in ext_to_fmt.keys() else ""
