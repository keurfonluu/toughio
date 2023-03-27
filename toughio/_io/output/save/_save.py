import numpy as np

from ...input import tough
from .._common import Output, reorder_labels

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order):
    """
    Read SAVE file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_type : str
        Input file type.
    file_format : str
        Input file format.
    labels_order : list of array_like
        List of labels.

    Returns
    -------
    namedtuple or list of namedtuple
        namedtuple (type, format, time, labels, data) or list of namedtuple for each time step.

    """
    parameters = tough.read(filename)

    labels = list(parameters["initial_conditions"])
    variables = [v["values"] for v in parameters["initial_conditions"].values()]

    data = {f"X{i + 1}": x for i, x in enumerate(np.transpose(variables))}

    data["porosity"] = np.array(
        [v["porosity"] for v in parameters["initial_conditions"].values()]
    )

    userx = [
        v["userx"] for v in parameters["initial_conditions"].values() if "userx" in v
    ]
    if userx:
        data["userx"] = np.array(userx)

    labels_order = labels_order if labels_order else parameters["initial_conditions"]
    output = Output(file_type, file_format, None, np.array(labels), data)
    return reorder_labels(output, labels_order)
