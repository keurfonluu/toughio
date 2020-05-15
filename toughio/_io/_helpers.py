from __future__ import with_statement

import collections

import numpy

from . import json, tough
from ._output import read_eleme

__all__ = [
    "Output",
    "read_history",
    "read_input",
    "write_input",
    "read_output",
    "read_save",
]


Output = collections.namedtuple("Output", ["type", "time", "labels", "data"])


_extension_to_filetype = {
    ".json": "json",
}


def _filetype_from_filename(filename):
    """Determine file type from its extension."""
    import os

    ext = os.path.splitext(filename)[1].lower()
    return (
        _extension_to_filetype[ext] if ext in _extension_to_filetype.keys() else "tough"
    )


def read_input(filename, file_format="tough", **kwargs):
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str
        Input file name.
    file_format : str ('tough', 'json'), optional, default 'tough'
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
    if file_format not in {"tough", "json"}:
        raise ValueError()

    fmt = file_format if file_format else _filetype_from_filename(filename)

    format_to_reader = {
        "tough": (tough, (), {}),
        "json": (json, (), {}),
    }
    interface, args, default_kwargs = format_to_reader[fmt]
    _kwargs = default_kwargs.copy()
    _kwargs.update(kwargs)
    return interface.read(filename, *args, **_kwargs)


def write_input(filename, parameters, file_format="tough", **kwargs):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str
        Output file name.
    parameters : dict
        Parameters to export.
    file_format : str ('tough', 'json'), optional, default 'tough'
        Output file format.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not isinstance(parameters, dict):
        raise TypeError()
    if file_format not in {"tough", "json"}:
        raise ValueError()

    fmt = file_format if file_format else _filetype_from_filename(filename)

    format_to_writer = {
        "tough": (tough, (), {}),
        "json": (json, (), {}),
    }
    interface, args, default_kwargs = format_to_writer[fmt]
    _kwargs = default_kwargs.copy()
    _kwargs.update(kwargs)
    interface.write(filename, parameters, *args, **_kwargs)


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


def read_output(filename, file_format="tough", labels_order=None):
    """
    Read TOUGH output file for each time step.

    Parameters
    ----------
    filename : str
        Input file name.
    file_format : str ('tough' or 'tecplot'), optional, default 'tough'
        TOUGH output file format.
    labels_order : list of array_like or None, optional, default None
        List of labels.

    Returns
    -------
    list of namedtuple
        List of namedtuple (type, time, labels, data) for each time step.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if file_format not in {"tough", "tecplot"}:
        raise ValueError()
    if not (
        labels_order is None or isinstance(labels_order, (list, tuple, numpy.ndarray))
    ):
        raise TypeError()

    headers, times, labels, variables = read_eleme(filename, file_format)
    outputs = [
        Output(
            "element",
            time,
            numpy.array(label),
            {k: v for k, v in zip(headers, numpy.transpose(variable))},
        )
        for time, label, variable in zip(times, labels, variables)
    ]
    return (
        [_reorder_labels(out, labels_order) for out in outputs]
        if labels_order is not None
        else outputs
    )


def read_save(filename, labels_order=None):
    """
    Read TOUGH SAVE file.

    Parameters
    ----------
    filename : str
        Input file name.
    labels_order : list of array_like or None, optional, default None
        List of labels.

    Returns
    -------
    list of namedtuple
        SAVE data as namedtuple (type, time, labels, data).

    Note
    ----
    Does not support hysteresis values yet.

    """
    if not isinstance(filename, str):
        raise TypeError()
    if not (
        labels_order is None or isinstance(labels_order, (list, tuple, numpy.ndarray))
    ):
        raise TypeError()

    with open(filename, "r") as f:
        # Check first line
        line = f.readline()
        if not line.startswith("INCON"):
            raise ValueError("Invalid SAVE file '{}'.".format(filename))

    parameters = read_input(filename)
    labels = list(parameters["initial_conditions"].keys())
    variables = [v["values"] for v in parameters["initial_conditions"].values()]

    data = {"X{}".format(i + 1): x for i, x in enumerate(numpy.transpose(variables))}

    data["porosity"] = numpy.array(
        [v["porosity"] for v in parameters["initial_conditions"].values()]
    )

    userx = [
        v["userx"]
        for v in parameters["initial_conditions"].values()
        if "userx" in v.keys()
    ]
    if userx:
        data["userx"] = numpy.array(userx)

    labels_order = (
        labels_order if labels_order else parameters["initial_conditions_order"]
    )
    output = Output("save", None, numpy.array(labels), data)
    return _reorder_labels(output, labels_order)


def _reorder_labels(data, labels):
    """Reorder output or save cell data according to input labels."""
    if len(data.labels) != len(labels):
        raise ValueError()

    mapper = {k: v for v, k in enumerate(data.labels)}
    idx = [mapper[label] for label in labels]
    data.labels[:] = data.labels[idx]

    for k, v in data.data.items():
        data.data[k] = v[idx]

    return data
