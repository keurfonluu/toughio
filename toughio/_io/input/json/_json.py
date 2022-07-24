import json

import numpy as np

from ...._common import open_file

__all__ = [
    "read",
    "write",
]


def read(filename):
    """
    Import json TOUGH input file.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    dict
        TOUGH input parameters.

    """

    def to_int(data):
        """Return dict with integer keys instead of strings."""
        return {int(k): data[k] for k in sorted(data)}

    with open_file(filename, "r") as f:
        parameters = json.load(f)

    if "react" in parameters and "options" in parameters["react"]:
        parameters["react"]["options"] = to_int(parameters["react"]["options"])

    if "extra_options" in parameters:
        parameters["extra_options"] = to_int(parameters["extra_options"])

    if "more_options" in parameters:
        parameters["more_options"] = to_int(parameters["more_options"])

    if "selections" in parameters:
        parameters["selections"]["integers"] = to_int(
            parameters["selections"]["integers"]
        )

    return parameters


def write(filename, parameters):
    """
    Export TOUGH parameters to json.

    Parameters
    ----------
    filename : str
        Output file name.
    parameters : dict
        Parameters to export.

    """
    from copy import deepcopy

    def jsonify(x):
        """JSON serialize data."""
        if isinstance(x, (np.int32, np.int64)):
            return int(x)
        elif isinstance(x, (list, tuple)):
            return [jsonify(xx) for xx in x]
        elif isinstance(x, np.ndarray):
            return x.tolist()
        elif isinstance(x, dict):
            return {k: jsonify(v) for k, v in x.items()}
        else:
            return x

    with open_file(filename, "w") as f:
        parameters = deepcopy(parameters)
        parameters = jsonify(parameters)
        json.dump(parameters, f, indent=4)
