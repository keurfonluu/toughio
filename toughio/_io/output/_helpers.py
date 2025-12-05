from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Literal, Optional, TextIO

import numpy as np
from numpy.typing import ArrayLike

from ..._common import filetype_from_filename, open_file, register_format
from ...core import Output


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}


def register(file_format, extensions, reader, writer=None):
    """
    Register a new output format.

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


def read(
    filename: str | os.PathLike | TextIO,
    file_format: Optional[
        Literal["csv", "petrasim", "save", "tecplot", "tough"]
    ] = None,
    labels_order: Optional[Sequence[ArrayLike]] = None,
    time_steps: Optional[int | Sequence[int]] = None,
    connection: bool = False,
) -> Output | list[Output]:
    """
    Read TOUGH SAVE or output file for each time step.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Input file name or buffer.
    file_format : {'csv', 'petrasim', 'save', 'tecplot', 'tough'}, optional
        Input file format.
    labels_order : Sequence[ArrayLike], optional
        List of labels. If None, output will be assumed ordered.
    time_steps : int | Sequence[int], optional
        List of time steps to read. If None, all time steps will be read.
    connection : bool, default False
        Only for standard TOUGH output file. If `True`, return data related to connections.

    Returns
    -------
    toughio.ElementOutput | toughio.ConnectionOutput | list[toughio.ElementOutput] | list[toughio.ConnectionOutput]
        Output data for each time step.

    """
    if not (
        labels_order is None or isinstance(labels_order, (list, tuple, np.ndarray))
    ):
        raise TypeError()

    if file_format is None:
        # Guess type and format from content
        file_type, file_format = get_output_type(filename)

        # Otherwise, guess file format from extension
        file_format = (
            file_format
            if file_format
            else filetype_from_filename(filename, _extension_to_filetype, "")
        )

    else:
        if file_format not in _reader_map:
            raise ValueError()

        file_type = "element"  # By default

    if connection:
        file_type = "connection" if connection else "element"

    return _reader_map[file_format](filename, file_type, labels_order, time_steps)


def write(filename, output, file_format=None, **kwargs):
    """
    Write TOUGH output file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    output : :class:`toughio.ElementOutput`, :class:`toughio.ConnectionOutput`, sequence of :class:`toughio.ElementOutput` or sequence of :class:`toughio.ConnectionOutput`
        Output data to export for each time step.
    file_format : {'csv', 'petrasim', 'tecplot'} or None, optional, default None
        Output file format.

    Other Parameters
    ----------------
    unit : dict or None, optional, default None
        Only if ``file_format = "tough"``. Overwrite header unit.

    """
    output = [output] if isinstance(output, Output) else output
    if not (
        isinstance(output, (list, tuple))
        and all(isinstance(out, Output) for out in output)
    ):
        raise TypeError()

    fmt = (
        file_format
        if file_format
        else filetype_from_filename(filename, _extension_to_filetype, "tough")
    )

    return _writer_map[fmt](filename, output, **kwargs)


def get_output_type(filename):
    """Get output file type and format."""
    with open_file(filename, "r") as f:
        line = f.readline().strip()

        if not line:
            line = f.readline().strip()
            if line.startswith("@@@@@"):
                file_format = "tough"
                file_type = "element"

            else:
                raise ValueError()

        elif line.startswith("1      @@@@@"):
            file_format = "tough"
            file_type = "element"

        elif line.startswith("INCON"):
            file_format = "save"
            file_type = "element"

        elif "=" in line:
            file_format = "tecplot"
            file_type = (
                "connection"
                if "HEAT" in line or "FLOW" in line or "VEL" in line
                else "element"
            )

        elif line.startswith("TIME"):
            file_format = "petrasim"
            file_type = "connection" if "ELEM1" in line else "element"

        else:
            header = line.split(",")[0].replace('"', "").strip()
            file_format = "csv"
            file_type = "connection" if header == "ELEM1" else "element"

            if header == "ELEM":
                file_format = "csv"
                file_type = "element"

            elif header == "ELEM1":
                file_format = "csv"
                file_type = "connection"

            else:
                file_format = "element"
                file_type = None

    return file_type, file_format
