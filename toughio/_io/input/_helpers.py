from __future__ import annotations

import os
import pathlib
from collections.abc import Callable, Sequence
from io import TextIOWrapper
from typing import Literal, Optional, TextIO

from ..._common import filetype_from_filename, register_format


def read(
    filename: str | os.PathLike | TextIO,
    file_format: Optional[
        Literal[
            "tough",
            "tough3",
            "tough4",
            "toughreact-flow",
            "toughreact-solute",
            "toughreact-chemical",
            "json",
        ]
    ] = None,
    **kwargs,
):
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Input file name or buffer.
    file_format : {'tough', 'tough3', 'tough4', 'toughreact-flow', 'toughreact-solute', 'toughreact-chemical', 'json'}, optional
        Input file format.
    **kwargs, dict
        Additional keyword arguments passed to the reader function.

    Returns
    -------
    dict
        TOUGH input parameters.

    """
    file_format, simulator = _get_file_format_simulator(filename, file_format)

    return _reader_map[file_format](filename, simulator=simulator, **kwargs)


def write(
    filename: str | os.PathLike | TextIO,
    parameters: dict,
    file_format: Optional[
        Literal[
            "tough",
            "tough3",
            "tough4",
            "toughreact-flow",
            "toughreact-solute",
            "toughreact-chemical",
            "json",
        ]
    ] = None,
    **kwargs,
):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Output file name or buffer.
    parameters : dict
        Parameters to export.
    file_format : {'tough', 'tough3', 'tough4', 'toughreact-flow', 'toughreact-solute', 'toughreact-chemical', 'json'}, optional
        Output file format.
    **kwargs, dict
        Additional keyword arguments passed to the writer function.

    """
    file_format, simulator = _get_file_format_simulator(filename, file_format)
    _writer_map[file_format](filename, parameters, simulator=simulator, **kwargs)


def _get_file_format_simulator(
    filename: str | os.PathLike,
    file_format: str | None,
    default: str = "tough",
) -> tuple[str, str]:
    """Get file format."""
    if not file_format and not isinstance(filename, TextIOWrapper):
        filename = pathlib.Path(filename).name
        file_format = _filename_to_file_format.get(filename)

    if not file_format:
        file_format = filetype_from_filename(filename, _extension_to_filetype, default)

    if not file_format:
        file_format = "tough"

    return file_format, _file_format_to_simulator.get(file_format, "tough")


def register(
    file_format: str,
    extensions: Sequence[str],
    reader: Callable,
    writer: Optional[Callable] = None,
) -> None:
    """
    Register a new input format.

    Parameters
    ----------
    file_format : str
        File format to register.
    extensions : Sequence[str]
        List of extensions to associate to the new format.
    reader : Callable
        Read function.
    writer : Callable, optional
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


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}

_filename_to_file_format = {
    "INFILE": "tough",
    "MESH": "tough",
    "INCON": "tough",
    "GENER": "tough",
    "flow.inp": "toughreact-flow",
    "solute.inp": "toughreact-solute",
    "chemical.inp": "toughreact-chemical",
}

_file_format_to_simulator = {
    "tough": "tough",
    "toughreact-flow": "toughreact",
    "toughreact-solute": "toughreact",
    "toughreact-chemical": "toughreact",
    "tough3": "tough3",
    "tough4": "tough4",
}
