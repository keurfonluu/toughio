import os

import numpy

import toughio

hybrid_mesh = toughio.Mesh(
    points=numpy.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
            [0.5, 0.5, 1.5],
            [0.0, 0.5, 1.5],
            [1.0, 0.5, 1.5],
            [2.0, 0.0, 0.0],
            [2.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [-1.0, 1.0, 0.0],
        ]
    ),
    cells=[
        ("hexahedron", numpy.array([[0, 1, 2, 3, 4, 5, 6, 7]])),
        ("pyramid", numpy.array([[4, 5, 6, 7, 8]])),
        ("tetra", numpy.array([[4, 8, 7, 9], [5, 6, 8, 10]])),
        ("wedge", numpy.array([[1, 11, 5, 2, 12, 6], [13, 0, 4, 14, 3, 7]])),
    ],
)


def relative_permeability(model, parameters, sl=None, atol=1.0e-8):
    import json

    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        this_dir, "support_files", "relative_permeability_references.json"
    )
    with open(filename, "r") as f:
        relperm_ref = json.load(f)

    sl = numpy.linspace(0.0, 1.0, 201) if sl is None else sl

    perm = model(*parameters)
    relperm = numpy.transpose(perm(sl))
    assert numpy.allclose(relperm, relperm_ref[perm.name], atol=atol)


def capillarity(model, parameters, sl=None, atol=1.0e-8):
    import json

    this_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(this_dir, "support_files", "capillarity_references.json")
    with open(filename, "r") as f:
        pcap_ref = json.load(f)

    sl = numpy.linspace(0.0, 1.0, 51) if sl is None else sl

    cap = model(*parameters)
    pcap = cap(sl)
    assert numpy.allclose(pcap, pcap_ref[cap.name][: len(pcap)], atol=atol)
