from __future__ import with_statement

import collections

import numpy

__all__ = [
    "read_output",
]


def read_output(filename):
    """
    Read TOUGH output file for each time step.

    Parameters
    ----------
    filename : str
        Input file name.

    Returns
    -------
    list of namedtuple
        List of namedtuple (time, labels, data) for each time step.
    """
    assert isinstance(filename, str)

    with open(filename, "r") as f:
        # Read header
        line = f.readline().replace('"', "")
        headers = [l.strip() for l in line.split(",")]

        # Skip second line (unit)
        line = f.readline()

        # Read data
        times, variables = [], []
        labels = []
        line = f.readline().replace('"', "").strip()
        while line:
            line = line.split(",")

            # Time step
            if line[0].startswith("TIME"):
                line = line[0].split()
                times.append(float(line[-1]))
                variables.append([])
                labels.append([])

            # Output
            else:
                labels[-1].append(line[0].strip())
                variables[-1].append([float(l.strip()) for l in line[1:]])

            line = f.readline().strip().replace('"', "")

    Output = collections.namedtuple("Output", ["time", "labels", "data"])

    return [
        Output(time, label, {
            k: v for k, v in zip(headers[1:], numpy.transpose(variable))
        }) for time, label, variable in zip(times, labels, variables)
    ]