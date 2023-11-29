import collections
import logging

import numpy as np

__all__ = [
    "Output",
]


Output = collections.namedtuple("Output", ["type", "time", "labels", "data"])


def to_output(file_type, labels_order, headers, times, labels, variables):
    """Create an Output namedtuple."""
    outputs = [
        Output(
            file_type,
            time,
            np.array(label) if len(label) else np.array(label, dtype="<U1"),
            {k: v for k, v in zip(headers, np.transpose(variable))},
        )
        for time, label, variable in zip(times, labels, variables)
    ]

    # Some older versions of TOUGH3 have duplicate connection outputs when running in parallel
    # Fix the outputs here by summing the duplicate connections
    if file_type == "connection" and len(labels[0]):
        # Check whether there are duplicate connections
        connections = {}

        for i, (c1, c2) in enumerate(outputs[0].labels):
            if (c1, c2) in connections:
                connections[(c1, c2)].append(i)
                found_duplicate = True

            else:
                connections[(c1, c2)] = [i]

        if found_duplicate:
            logging.warning(
                "Found duplicate connections. Fixing outputs by summing duplicate connections."
            )

            outputs = [
                Output(
                    output.type,
                    output.time,
                    np.array(list(connections)),
                    {
                        k: np.array([v[idx].sum() for idx in connections.values()])
                        for k, v in output.data.items()
                    },
                )
                for output in outputs
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
