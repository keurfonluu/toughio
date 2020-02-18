from __future__ import with_statement

import collections

import numpy

from . import json, tough

__all__ = [
    "Output",
    "Save",
    "read_input",
    "write_input",
    "read_output",
    "read_save",
]


Output = collections.namedtuple("Output", ["time", "labels", "data"])
Save = collections.namedtuple("Save", ["labels", "data"])


_extension_to_filetype = {
    ".json": "json",
}


def _filetype_from_filename(filename):
    """
    Determine file type from its extension.
    """
    import os

    ext = os.path.splitext(filename)[1].lower()
    return (
        _extension_to_filetype[ext] if ext in _extension_to_filetype.keys() else "tough"
    )


def read_input(filename, file_format="json", **kwargs):
    """Read TOUGH input file.

    Parameters
    ----------
    filename : str
        Input file name.
    file_format : str ('tough', 'json'), optional, default 'json'
        Input file format.
    
    Returns
    -------
    dict
        TOUGH input parameters.
    
    """
    assert isinstance(filename, str)
    assert file_format in {"tough", "json"}

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
    """Write TOUGH input file.

    Parameters
    ----------
    filename : str
        Output file name.
    parameters : dict
        Parameters to export.
    file_format : str ('tough', 'json'), optional, default 'tough'
        Output file format.
    
    """
    assert isinstance(filename, str)
    assert isinstance(parameters, dict)
    assert file_format in {"tough", "json"}

    fmt = file_format if file_format else _filetype_from_filename(filename)

    format_to_writer = {
        "tough": (tough, (), {}),
        "json": (json, (), {}),
    }
    interface, args, default_kwargs = format_to_writer[fmt]
    _kwargs = default_kwargs.copy()
    _kwargs.update(kwargs)
    interface.write(filename, parameters, *args, **_kwargs)


def read_output(filename):
    """Read TOUGH output file for each time step.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    list of namedtuple
        List of namedtuple (time, labels, data) for each time step.
    
    """
    assert isinstance(filename, str)

    with open(filename, "r") as f:
        # Read header
        line = f.readline().replace('"', "")
        headers = [l.strip() for l in line.split(",")]

        # Skip second line (unit)
        line = f.readline()

        # Check third line (does it starts with TIME?)
        i = f.tell()
        line = f.readline()
        f.seek(i)
        single = not line.startswith('"TIME')

        # Read data
        if single:
            times, labels, variables = [None], [[]], [[]]
        else:
            times, labels, variables = [], [], []
        line = f.readline().replace('"', "").strip()
        while line:
            line = line.split(",")

            # Time step
            if line[0].startswith("TIME"):
                line = line[0].split()
                times.append(float(line[-1]))
                variables.append([])
                labels.append([])

            # Output
            else:
                labels[-1].append(line[0].strip())
                variables[-1].append([float(l.strip()) for l in line[1:]])

            line = f.readline().strip().replace('"', "")

    return [
        Output(
            time, label, {k: v for k, v in zip(headers[1:], numpy.transpose(variable))}
        )
        for time, label, variable in zip(times, labels, variables)
    ]


def read_save(filename):
    """Read TOUGH SAVE file.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    list of namedtuple
        SAVE data as namedtuple (labels, data).

    Note
    ----
    Does not support porosity, USERX and hysteresis values yet.
    
    """

    def str2float(s):
        """
        Convert primary variables string to float.
        """
        s = s.lower()
        significand, exponent = s[:-4], s[-4:].replace("e", "")
        return float("{}e{}".format(significand, exponent))

    assert isinstance(filename, str)

    with open(filename, "r") as f:
        # Check first line
        line = f.readline()
        assert line.startswith("INCON"), "Invalid SAVE file '{}'.".format(filename)

        # Read data
        labels, variables = [], []
        line = f.readline().strip()
        while line:
            # Label
            line = line.split()
            labels.append(line[0])

            # Primary variables
            line = f.readline().strip().split()
            variables.append([str2float(l) for l in line])

            line = f.readline().strip()
            if line.startswith("+++"):
                break

    return Save(
        labels,
        {"X{}".format(i + 1): x for i, x in enumerate(numpy.transpose(variables))},
    )
