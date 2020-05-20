from __future__ import with_statement

import numpy

__all__ = [
    "read",
    "read_history",
]


_reader_map = {}
_writer_map = {}


def register(file_format, reader, writer=None):
    """Register a new format."""
    _reader_map[file_format] = reader
    if writer is not None:
        _writer_map[file_format] = writer


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
        elif line.startswith("INCON"):
            return "element", "save"
        elif "=" in line:
            return "element", "tecplot"
        else:
            header = line.split(",")[0].replace('"', "").strip()
            
            if header == "ELEM":
                return "element", "csv"
            elif header == "ELEM1":
                return "connection", "csv"
            else:
                raise ValueError()


def read(filename, labels_order=None):
    """
    Read TOUGH SAVE or output file for each time step.

    Parameters
    ----------
    filename : str
        Input file name.
    labels_order : list of array_like or None, optional, default None
        List of labels.

    Returns
    -------
    namedtuple or list of namedtuple
        namedtuple (type, time, labels, data) or list of namedtuple for each time step.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (
        labels_order is None or isinstance(labels_order, (list, tuple, numpy.ndarray))
    ):
        raise TypeError()

    file_type, file_format = get_output_type(filename)

    return _reader_map[file_format](filename, file_type, file_format, labels_order)


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
        headers = line.split()[1:]

        data = []
        line = f.readline().strip()
        while line:
            data += [[float(x) for x in line.split()]]
            line = f.readline().strip()
        data = numpy.transpose(data)

        out = {"TIME": data[0]}
        for header, X in zip(headers, data[1:]):
            out[header] = X

        return out
