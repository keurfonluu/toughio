import os

import numpy

import toughio


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
