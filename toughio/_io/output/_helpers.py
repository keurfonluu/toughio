from __future__ import with_statement

import numpy as np

from ..._common import filetype_from_filename, register_format
from ._common import Output

__all__ = [
    "register",
    "read",
    "write",
    "read_history",
]


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
        Read fumction.
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


def get_output_type(filename):
    """Get output file type and format."""
    with open(filename, "r") as f:
        line = f.readline().strip()

        if not line:
            line = f.readline().strip()
            if line.startswith("@@@@@"):
                return "element", "tough"
            else:
                raise ValueError()
        elif line.startswith("1      @@@@@"):
            return "element", "tough"
        elif line.startswith("INCON"):
            return "element", "save"
        elif "=" in line:
            return "element", "tecplot"
        elif line.startswith("TIME"):
            return "element", "petrasim"
        else:
            header = line.split(",")[0].replace('"', "").strip()

            if header == "ELEM":
                return "element", "csv"
            elif header == "ELEM1":
                return "connection", "csv"
            else:
                raise ValueError()


def read(filename, labels_order=None, connection=False, label_length=None, **kwargs):
    """
    Read TOUGH SAVE or output file for each time step.

    Parameters
    ----------
    filename : str
        Input file name.
    labels_order : list of array_like or None, optional, default None
        List of labels.
    connection : bool, optional, default False
        Only for standard TOUGH output file. If `True`, return data related to connections.
    label_length : int or None, optional, default None
        Only for standard TOUGH output file. Number of characters in cell labels.

    Returns
    -------
    namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (
        labels_order is None or isinstance(labels_order, (list, tuple, np.ndarray))
    ):
        raise TypeError()

    file_type, file_format = get_output_type(filename)
    file_type = "connection" if (file_format == "tough" and connection) else file_type

    _kwargs = {"label_length": label_length} if file_format == "tough" else {}
    _kwargs.update(kwargs)
    return _reader_map[file_format](
        filename, file_type, file_format, labels_order, **_kwargs
    )


def write(filename, output, file_format=None, **kwargs):
    """
    Write TOUGH output file.

    Parameters
    ----------
    filename : str
        Input file name.
    output : namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step to export.
    file_format : str or None, optional, default None
        Output file format.
    
    Other Parameters
    ----------------
    unit : dict or None, optional, default None
        Only if ``file_format = "tough"``. Overwrite header unit.

    """
    if not isinstance(filename, str):
        raise TypeError()

    output = [output] if isinstance(output, Output) else output
    if not (
        isinstance(output, (list, tuple))
        and all(isinstance(out, Output) for out in output)
    ):
        raise TypeError()

    fmt = (
        file_format
        if file_format
        else filetype_from_filename(filename, _extension_to_filetype)
    )

    return _writer_map[fmt](filename, output, **kwargs)


def read_history(filename):
    """
    Read history file.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    dict
        History data.

    """
    if not isinstance(filename, str):
        raise TypeError()

    with open(filename, "r") as f:
        line = f.readline().strip()

        if line.startswith('"'):
            sep = ","
            line = line.replace('"', "")
        else:
            sep = None
        headers = [x.strip() for x in line.split(sep)[1:]]

        data = []
        line = f.readline().strip()
        while line:
            data += [[float(x) for x in line.split(sep)]]
            line = f.readline().strip()
        data = np.transpose(data)

        out = {"TIME": data[0]}
        for header, X in zip(headers, data[1:]):
            out[header] = X

        return out
