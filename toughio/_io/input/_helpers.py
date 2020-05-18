import os

__all__ = [
    "read",
    "write",
]


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}


def register(name, extensions, reader, writer_map):
    """Register a new format."""
    for ext in extensions:
        _extension_to_filetype[ext] = name

    if reader is not None:
        _reader_map[name] = reader
    _writer_map.update(writer_map)


def _filetype_from_filename(filename):
    """Determine file type from its extension."""
    ext = os.path.splitext(filename)[1].lower()
    return (
        _extension_to_filetype[ext] if ext in _extension_to_filetype.keys() else "tough"
    )


def read(filename, file_format=None, **kwargs):
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str
        Input file name.
    file_format : str ('tough', 'json') or None, optional, default None
        Input file format.

    Returns
    -------
    dict
        TOUGH input parameters.

    Note
    ----
    If ``file_format == 'tough'``, can also read `MESH`, `INCON` and `GENER` files.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (file_format is None or file_format in {"tough", "json"}):
        raise ValueError()

    fmt = file_format if file_format else _filetype_from_filename(filename)

    return _reader_map[fmt](filename, **kwargs)


def write(filename, parameters, file_format=None, **kwargs):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str
        Output file name.
    parameters : dict
        Parameters to export.
    file_format : str ('tough', 'json') or None, optional, default None
        Output file format.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not isinstance(parameters, dict):
        raise TypeError()
    if not (file_format is None or file_format in {"tough", "json"}):
        raise ValueError()

    fmt = file_format if file_format else _filetype_from_filename(filename)

    _writer_map[fmt](filename, parameters, **kwargs)
