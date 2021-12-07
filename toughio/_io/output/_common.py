import collections

import numpy as np

__all__ = [
    "Output",
]


Output = collections.namedtuple("Output", ["type", "format", "time", "labels", "data"])


def to_output(file_type, file_format, labels_order, headers, times, labels, variables):
    """Create an Output namedtuple."""
    outputs = [
        Output(
            file_type,
            file_format,
            time,
            np.array(label),
            {k: v for k, v in zip(headers, np.transpose(variable))},
        )
        for time, label, variable in zip(times, labels, variables)
    ]
    return (
        [reorder_labels(out, labels_order) for out in outputs]
        if labels_order is not None and file_type == "element"
        else outputs
    )


def reorder_labels(data, labels):
    """Reorder output or save cell data according to input labels."""
    if len(data.labels) != len(labels):
        raise ValueError()

    mapper = {k: v for v, k in enumerate(data.labels)}
    idx = [mapper[label] for label in labels]
    data.labels[:] = data.labels[idx]

    for k, v in data.data.items():
        data.data[k] = v[idx]

    return data
