import logging

import numpy as np

from ...core import ConnectionOutput, ElementOutput


def to_output(file_type, labels_order, headers, times, labels, data, return_list):
    """Helper function to create output data objects."""
    outputs = []
    for time, labels_, data_ in zip(times, labels, data):
        kwargs = {
            "data": {k: v for k, v in zip(headers, np.transpose(data_))},
            "time": time,
            "labels": labels_ if labels_ is not None and len(labels_) else None,
        }

        output = (
            ElementOutput(**kwargs)
            if file_type == "element"
            else ConnectionOutput(**kwargs)
        )
        outputs.append(output)

    # Some older versions of TOUGH3 have duplicate connection outputs when running in parallel
    # Fix the outputs here by keeping the first occurence (the other occurrences should hold the same values)
    if file_type == "connection" and len(labels[0]):
        # Check whether there are duplicate connections
        connections = {}
        found_duplicate = False

        for i, (c1, c2) in enumerate(outputs[0].labels):
            if (c1, c2) in connections:
                connections[(c1, c2)].append(i)
                found_duplicate = True

            else:
                connections[(c1, c2)] = [i]

        if found_duplicate:
            outputs = [
                ConnectionOutput(
                    data={
                        k: np.array([v[idx[0]] for idx in connections.values()])
                        for k, v in output.data.items()
                    },
                    time=output.time,
                    labels=list(connections),
                )
                for output in outputs
            ]

    if file_type == "element" and labels_order is not None:
        outputs = [output[labels_order] for output in outputs]

    return outputs if return_list else outputs[0]
