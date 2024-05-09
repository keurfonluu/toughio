import numpy as np

from ...input import tough
from .._common import ElementOutput

__all__ = [
    "read",
]


def read(filename, file_type=None, labels_order=None):
    """
    Read SAVE file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_type : str or None, default, None
        Input file type.
    labels_order : list of array_like
        List of labels. If None, output will be assumed ordered.

    Returns
    -------
    :class:`toughio.ElementOutput`
        Output data.

    """
    parameters = tough.read(filename)
    
    data = [v["values"] for v in parameters["initial_conditions"].values()]
    data = {f"X{i + 1}": x for i, x in enumerate(np.transpose(data))}
    data["porosity"] = np.array(
        [v["porosity"] for v in parameters["initial_conditions"].values()]
    )
    labels = list(parameters["initial_conditions"])

    userx = [
        v["userx"] for v in parameters["initial_conditions"].values() if "userx" in v
    ]
    if userx:
        data["userx"] = np.array(userx)

    try:
        time = float(parameters["end_comments"][1].split()[-1])

    except Exception:
        time = None

    output = ElementOutput(time, data, labels)

    return output
