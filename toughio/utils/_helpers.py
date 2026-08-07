from __future__ import annotations

from typing import TYPE_CHECKING

import glob
import numpy as np
import os
import pathlib
import tarfile

from ..core import H5File, Mesh


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Literal, Optional

    from .. import HistoryOutput, RockHistoryOutput


def dump_outputs(
    filename: str | os.PathLike,
    path: Optional[str | os.PathLike] = None,
    with_mesh: Optional[str | os.PathLike | Mesh] = None,
    connection_output_pattern: Optional[str] = None,
    element_output_pattern: Optional[str] = None,
    connection_history_pattern: Optional[str] = None,
    element_history_pattern: Optional[str] = None,
    generator_history_pattern: Optional[str] = None,
    rock_history_pattern: Optional[str] = None,
    compression: Optional[Literal["gzip", "lzf"]] = None,
    compression_opts: Optional[int] = None,
    exist_ok: bool = False,
    tar: bool = False,
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
    with_mesh : str | PathLike | toughio.Mesh
        Mesh to export.
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
    compression : {'gzip', 'lzf'}, optional, default 'lzf'
        Compression algorithm to use.
    compression_opts : int, optional, default 4
        Compression level for gzip compression. May be an integer from 0 to 9.
    exist_ok : bool, default False
        If True, overwrite *filename* if it already exists.
    tar : bool, default False
        If True, move dumped files to a tarball.
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
        connection_output_pattern if connection_output_pattern else "OUTPUT_CONNE*"
    )
    connection_output_filenames = sorted(glob.glob(str(connection_output_pattern)))

    element_output_pattern = path / (
        element_output_pattern if element_output_pattern else "OUTPUT_ELEME*"
    )
    element_output_filenames = sorted(glob.glob(str(element_output_pattern)))

    connection_history_pattern = path / (
        connection_history_pattern if connection_history_pattern else "COFT_*"
    )
    connection_history_filenames = sorted(glob.glob(str(connection_history_pattern)))

    element_history_pattern = path / (
        element_history_pattern if element_history_pattern else "FOFT_*"
    )
    element_history_filenames = sorted(glob.glob(str(element_history_pattern)))

    generator_history_pattern = path / (
        generator_history_pattern if generator_history_pattern else "GOFT_*"
    )
    generator_history_filenames = sorted(glob.glob(str(generator_history_pattern)))

    rock_history_pattern = path / (
        rock_history_pattern if rock_history_pattern else "ROFT_*"
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

    with H5File(
        filename,
        mode="w",
        compression=compression,
        compression_opts=compression_opts,
        exist_ok=exist_ok,
    ) as f:
        if with_mesh:
            f.dump(Mesh(with_mesh))

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

    if tar:
        tar_filename = pathlib.Path(filename).with_suffix(".tar.gz")

        with tarfile.open(tar_filename, "w:gz") as tf:
            for filename_ in filenames_to_dump:
                tf.add(filename_, arcname=pathlib.Path(filename_).name)

        # Remove files only when the tarball is written
        for filename_ in filenames_to_dump:
            os.remove(filename_)

    if return_dumped_filenames:
        return filenames_to_dump


def load_element_history(
    filename: str | os.PathLike | Sequence[str | os.PathLike],
    names: Sequence[str] | dict[str, str],
    ignore_errors: bool = False,
) -> dict[str, HistoryOutput]:
    """
    Load and aggregate element history outputs from one or more H5 files.

    Parameters
    ----------
    filename : str | PathLike | Sequence[str | PathLike]
        H5 filename(s) to load element history outputs from. Files must be sorted in
        chronological order.
    names : Sequence[str] | dict[str, str]
        Labels of element to load element history outputs for.
    ignore_errors : bool, default False
        If True, ignore errors when loading element history outputs.

    Returns
    -------
    dict[str, toughio.HistoryOutput]
        Dictionary of aggregated element history outputs for each label.
    
    """
    from .. import H5File, HistoryOutput

    # Normalize inputs
    filenames = [filename] if isinstance(filename, (str, os.PathLike)) else filename
    names_ = (
        {name: name for name in names}
        if not isinstance(names, dict)
        else names
    )

    # Loop over files and names
    foft = {}

    for filename in filenames:
        with H5File(filename) as f:
            foft_list = set(f.list_element_history())

            for k, v in names_.items():
                v = v.replace(" ", "_")

                if v not in foft_list:
                    if ignore_errors:
                        continue

                    raise ValueError(f"could not find element history for label '{v}' in '{filename}'")

                foft_ = foft.setdefault(k, HistoryOutput())
                foft_ += f.load_element_history(v)

    return foft


def load_rock_history(
    filename: str | os.PathLike | Sequence[str | os.PathLike],
    names: Sequence[tuple[str, str]] | dict[str, Sequence[tuple[str, str]]],
    ignore_errors: bool = False,
) -> dict[str, RockHistoryOutput]:
    """
    Load and aggregate rock history outputs from one or more H5 files.

    Parameters
    ----------
    filename : str | PathLike | Sequence[str | PathLike]
        H5 filename(s) to load rock history outputs from. Files must be sorted in
        chronological order.
    names : Sequence[tuple[str, str]] | dict[str, Sequence[tuple[str, str]]]
        Interfaces to load rock history outputs for.
    ignore_errors : bool, default False
        If True, ignore errors when loading rock history outputs.

    Returns
    -------
    dict[str, RockHistoryOutput]
        Dictionary of aggregated rock history outputs for each interface.
    
    """
    from .. import H5File, RockHistoryOutput

    # Normalize inputs
    filenames = [filename] if isinstance(filename, (str, os.PathLike)) else filename
    names_ = (
        {"-".join(name): [name] for name in names}
        if not isinstance(names, dict)
        else {k: v for k, v in names.items()}
    )

    # Loop over files and interfaces
    roft = {}

    for filename in filenames:
        with H5File(filename) as f:
            roft_list = set(f.list_rock_history())

            for k, v in names_.items():
                for connection in v:
                    name = "-".join(connection)

                    if name not in roft_list:
                        if ignore_errors:
                            continue

                        raise ValueError(f"could not find rock history for interface '{name}' in '{filename}'")

                    roft_ = roft.setdefault(k, {}).setdefault(name, RockHistoryOutput())
                    roft_ += f.load_rock_history(name)

    return {
        k: RockHistoryOutput(
            {
                "TIME": next(iter(v.values())).data["TIME"],
                **{
                    k: np.sum([vv.data[k] for vv in v.values()], axis=0)
                    for k in next(iter(v.values())).data
                    if k != "TIME"
                }
            }
        )
        for k, v in roft.items()
    }
