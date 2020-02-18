from __future__ import with_statement

import json

__all__ = [
    "read",
    "write",
]


def read(filename):
    """Import json TOUGH input file.
    
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
        """Return dict with integer keys instead of strings.
        """
        return {int(k): data[k] for k in sorted(data.keys())}

    with open(filename, "r") as f:
        parameters = json.load(f)

    keys = {"extra_options", "more_options", "selections"}
    for key in keys:
        if key in parameters.keys():
            parameters[key] = to_int(parameters[key])

    return parameters


def write(filename, parameters):
    """Export TOUGH parameters to json.

    Parameters
    ----------
    filename : str
        Output file name.
    parameters : dict
        Parameters to export.
    """
    with open(filename, "w") as f:
        json.dump(parameters, f, indent=4)
