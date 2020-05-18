from __future__ import with_statement

import json

import numpy

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
        return {int(k): data[k] for k in sorted(data.keys())}

    with open(filename, "r") as f:
        parameters = json.load(f)

    if "extra_options" in parameters.keys():
        parameters["extra_options"] = to_int(parameters["extra_options"])

    if "more_options" in parameters.keys():
        parameters["more_options"] = to_int(parameters["more_options"])

    if "selections" in parameters.keys():
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
        if isinstance(x, (numpy.int32, numpy.int64)):
            return int(x)
        elif isinstance(x, (list, tuple)):
            return [jsonify(xx) for xx in x]
        elif isinstance(x, numpy.ndarray):
            return x.tolist()
        elif isinstance(x, dict):
            return {k: jsonify(v) for k, v in x.items()}
        else:
            return x

    with open(filename, "w") as f:
        parameters = deepcopy(parameters)
        parameters = jsonify(parameters)
        json.dump(parameters, f, indent=4)
