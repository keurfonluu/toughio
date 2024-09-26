from __future__ import annotations
from typing import Optional

import glob
import os
import pathlib

import numpy as np

from ..core import H5File


def dump_outputs(
    filename: str | os.PathLike,
    path: Optional[str | os.PathLike] = None,
    connection_output_pattern: Optional[str] = None,
    element_output_pattern: Optional[str] = None,
    connection_history_pattern: Optional[str] = None,
    element_history_pattern: Optional[str] = None,
    generator_history_pattern: Optional[str] = None,
    rock_history_pattern: Optional[str] = None,
    compression_opts: Optional[int] = None,
    exist_ok: bool = False,
    return_dumped_filenames: bool = False,
) -> list[str] | None:
    """
    Dump all outputs in a path to an H5 container.

    Parameters
    ----------
    filename : str | PathLike
        H5 container file name.
    path : str | PathLike
        Path of directory where outputs to be dumped are located.
    connection_output_pattern : str, optional
        Pattern used to find connection output file names.
    element_output_pattern : str, optional
        Pattern used to find element output file names.
    connection_history_pattern : str, optional
        Pattern used to find connection history file names.
    element_history_pattern : str, optional
        Pattern used to find element history file names.
    generator_history_pattern : str, optional
        Pattern used to find generator history file names.
    rock_history_pattern : str, optional
        Pattern used to find rock history file names.
    compression_opts : int, optional, default 4
        Compression level for gzip compression. May be an integer from 0 to 9.
    exist_ok : bool, default False
        If True, overwrite *filename* if it already exists.
    return_dumped_filenames : bool, default False
        If True, return a list of of the output file names that have been dumped.
    
    Returns
    -------
    sequence of str
        List of output file names that have been dumped. Only provided if *return_dumped_filenames* is True.
    
    """
    from .. import read_output, read_table

    path = pathlib.Path(path if path else ".")

    if not (path.exists() and path.is_dir()):
        raise ValueError(f"'{str(path)}' is not a directory")

    connection_output_pattern = path / (
        connection_output_pattern
        if connection_output_pattern
        else "OUTPUT_CONNE*"
    )
    connection_output_filenames = sorted(glob.glob(str(connection_output_pattern)))

    element_output_pattern = path / (
        element_output_pattern
        if element_output_pattern
        else "OUTPUT_ELEME*"
    )
    element_output_filenames = sorted(glob.glob(str(element_output_pattern)))

    connection_history_pattern = path / (
        connection_history_pattern
        if connection_history_pattern
        else "COFT_*"
    )
    connection_history_filenames = sorted(glob.glob(str(connection_history_pattern)))

    element_history_pattern = path / (
        element_history_pattern
        if element_history_pattern
        else "FOFT_*"
    )
    element_history_filenames = sorted(glob.glob(str(element_history_pattern)))

    generator_history_pattern = path / (
        generator_history_pattern
        if generator_history_pattern
        else "GOFT_*"
    )
    generator_history_filenames = sorted(glob.glob(str(generator_history_pattern)))

    rock_history_pattern = path / (
        rock_history_pattern
        if rock_history_pattern
        else "ROFT_*"
    )
    rock_history_filenames = sorted(glob.glob(str(rock_history_pattern)))

    filenames_to_dump = (
        connection_output_filenames
        + element_output_filenames
        + connection_history_filenames
        + element_history_filenames
        + generator_history_filenames
        + rock_history_filenames
    )

    if not filenames_to_dump:
        raise ValueError(f"could not find any output file in '{str(path)}'")
        
    with H5File(filename, mode="w", compression_opts=compression_opts, exist_ok=exist_ok) as f:
        for filename_ in connection_output_filenames:
            outputs = read_output(filename_, connection=True)

            for output in outputs:
                f.dump(output)

        for filename_ in element_output_filenames:
            outputs = read_output(filename_, connection=False)

            for output in outputs:
                f.dump(output)

        for filename_ in connection_history_filenames:
            output = read_table(filename_)
            f.dump(output)

        for filename_ in element_history_filenames:
            output = read_table(filename_)
            f.dump(output)

        for filename_ in generator_history_filenames:
            output = read_table(filename_)
            f.dump(output)

        for filename_ in rock_history_filenames:
            output = read_table(filename_)
            f.dump(output)

    if return_dumped_filenames:
        return filenames_to_dump
