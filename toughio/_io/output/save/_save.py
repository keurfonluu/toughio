from __future__ import with_statement

from .._common import Output, reorder_labels
from ...input import tough

import numpy

__all__ = [
    "read",
]


def read(filename, file_type, file_format, labels_order):
    """Read SAVE."""
    parameters = tough.read(filename)

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
    output = Output(file_type, file_format, None, numpy.array(labels), data)
    return reorder_labels(output, labels_order)
