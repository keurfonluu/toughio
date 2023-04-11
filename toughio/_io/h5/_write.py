import h5py
import pathlib

from ..output import Output
from ..output import read as read_output
from ..table import read as read_table


def write(
    filename,
    elements=None,
    connections=None,
    element_history=None,
    connection_history=None,
    generator_history=None,
    rock_history=None,
    labels_order=None,
    compression_opts=4,
):
    """
    Write TOUGH outputs to a HDF5 file.

    Parameters
    ----------
    filename : str or pathlike
        Output file name.
    elements : namedtuple, list of namedtuple, str, pathlike or None, optional, default None
    connections : namedtuple, list of namedtuple, str, pathlike or None, optional, default None
        Connection outputs to export.
    element_history : dict or None, optional, default None
        Element history to export.
    connection_history : dict or None, optional, default None
        Connection history to export.
    generator_history : dict or None, optional, default None
        Generator history to export.
    rock_history : dict or None, optional, default None
        Rock history to export.
    labels_order : list of array_like or None, optional, default None
        List of labels.
    compression_opts : int, optional, default 4
        Compression level for gzip compression. May be an integer from 0 to 9.
    
    """
    kwargs = {
        "compression": "gzip",
        "compression_opts": compression_opts,
    }

    with h5py.File(filename, "w") as f:
        if elements is not None:
            group = f.create_group("elements")
            _write_output(group, elements, labels_order, connection=False, **kwargs)

        if connections is not None:
            group = f.create_group("connections")
            _write_output(group, connections, labels_order, connection=True, **kwargs)

        if element_history is not None:
            group = f.create_group("element_history")
            _write_table(group, element_history, **kwargs)

        if connection_history is not None:
            group = f.create_group("connection_history")
            _write_table(group, connection_history, **kwargs)

        if generator_history is not None:
            group = f.create_group("generator_history")
            _write_table(group, generator_history, **kwargs)

        if rock_history is not None:
            group = f.create_group("rock_history")
            _write_table(group, rock_history, **kwargs)


def _write_output(f, outputs, labels_order, connection, **kwargs):
    """Write TOUGH output to group."""
    if isinstance(outputs, (str, pathlib.Path)):
        outputs = read_output(outputs, labels_order=labels_order, connection=connection)

    if isinstance(outputs, Output):
        outputs = [outputs]

    elif isinstance(outputs, (list, tuple)):
        for output in outputs:
            if not isinstance(output, Output):
                raise ValueError()
            
    else:
        raise ValueError()

    for output in outputs:
        group = f.create_group(f"time={output.time}")
        group.create_dataset("labels", data=output.labels.astype("S"), **kwargs)

        for k, v in output.data.items():
            group.create_dataset(k, data=v, **kwargs)


def _write_table(f, tables, **kwargs):
    """Write TOUGH table to group."""
    if not isinstance(tables, dict):
        raise ValueError()

    for name, table in tables.items():
        group = f.create_group(name)
        
        if isinstance(table, (str, pathlib.Path)):
            table = read_table(table)

        for k, v in table.items():
            group.create_dataset(k, data=v, **kwargs)
