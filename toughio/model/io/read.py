# -*- coding: utf-8 -*-

"""
Author: Keurfon Luu <keurfonluu@lbl.gov>
License: MIT
"""

import json

from .common import set_parameters

__all__ = [
    "read_json",
]


def read_json(filename, return_parameters = False):
    """
    Import TOUGH input file.
    
    Parameters
    ----------
    filename : str
        Input file name.
    return_parameters : bool, optional, default False
        If `True`, return parameters as a dict. Otherwise, overwrite
        current `toughio.model.Parameters`.
    
    Returns
    -------
    dict
        TOUGH input parameters. Only if ``return_parameters == True``.
    """
    def to_int(data):
        """
        Return dict with integer keys instead of strings.
        """
        return { int(k): data[k] for k in sorted(data.keys()) }
    
    assert isinstance(filename, str)
    with open(filename, "r") as f:
        parameters = json.load(f)

    if "extra_options" in parameters.keys():
        parameters["extra_options"] = to_int(parameters["extra_options"])
    if "selections" in parameters.keys():
        parameters["selections"] = to_int(parameters["selections"])

    if return_parameters:
        return parameters
    else:
        set_parameters(parameters)