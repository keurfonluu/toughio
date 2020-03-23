import os
import tempfile

import numpy

import toughio

numpy.random.seed(42)

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


def tempdir(filename=None):
    temp_dir = tempfile.mkdtemp()
    return os.path.join(temp_dir, filename) if filename else temp_dir


def write_read(filename, obj, writer, reader, writer_kws=None, reader_kws=None):
    writer_kws = writer_kws if writer_kws else {}
    reader_kws = reader_kws if reader_kws else {}

    filepath = tempdir(filename)
    if obj is not None:
        writer(filepath, obj, **writer_kws)
    else:
        writer(filepath, **writer_kws)

    return reader(filepath, **reader_kws)


def random_string(n):
    import random
    from string import ascii_lowercase

    return "".join(random.choice(ascii_lowercase) for _ in range(n))


def allclose_dict(a, b, atol=1.0e-8):
    for k, v in a.items():
        if v is not None:
            assert numpy.allclose(v, b[k], atol=atol)
        else:
            assert b[k] is None


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
