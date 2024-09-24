from __future__ import annotations
from typing import Callable, Literal, Optional, TextIO

import os

from ..._common import filetype_from_filename, register_format


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}


def register(
    file_format: str,
    extensions: list[str],
    reader: Callable,
    writer: Optional[Callable] = None,
) -> None:
    """
    Register a new table format.

    Parameters
    ----------
    file_format : str
        File format to register.
    extensions : ArrayLike
        List of extensions to associate to the new format.
    reader : callable
        Read function.
    writer : callable, optional
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


def read(
    filename: str | os.PathLike | TextIO,
    file_format: Optional[Literal["column", "csv", "tecplot"]] = None,
    **kwargs,
):
    """
    Read history file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        History file name or buffer.
    file_format : {'column', 'csv', 'tecplot'}, optional
        History file format.

    Returns
    -------
    :class:`toughio.HistoryOutput`
        History output data.

    """
    fmt = (
        file_format
        if file_format
        else filetype_from_filename(filename, _extension_to_filetype, "csv")
    )

    return _reader_map[fmt](filename, **kwargs)
