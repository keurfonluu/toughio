from ..._common import filetype_from_filename, register_format

__all__ = [
    "register",
    "read",
]


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}


def register(file_format, extensions, reader, writer=None):
    """
    Register a new table format.

    Parameters
    ----------
    file_format : str
        File format to register.
    extensions : array_like
        List of extensions to associate to the new format.
    reader : callable
        Read function.
    writer : callable or None, optional, default None
        Write function.

    """
    register_format(
        fmt=file_format,
        ext_to_fmt=_extension_to_filetype,
        reader_map=_reader_map,
        writer_map=_writer_map,
        extensions=extensions,
        reader=reader,
        writer=writer,
    )


def read(filename, file_format=None, **kwargs):
    """
    Read table file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_format : str ('column', 'csv', 'tecplot') or None, optional, default None
        Input file format.

    Returns
    -------
    dict
        Table data.

    """
    fmt = (
        file_format
        if file_format
        else filetype_from_filename(filename, _extension_to_filetype, "csv")
    )

    return _reader_map[fmt](filename, **kwargs)
