import os
import warnings
from functools import wraps

__all__ = [
    "register_format",
    "filetype_from_filename",
]


def register_format(fmt, ext_to_fmt, reader_map, writer_map, extensions, reader, writer):
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
