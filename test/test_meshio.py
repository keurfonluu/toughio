from copy import deepcopy

import numpy
import pytest

import helpers
import toughio

write_read = lambda mesh, writer_kws, reader_kws: helpers.write_read(
    "hybrid_mesh",
    mesh,
    toughio.write_mesh,
    toughio.read_mesh,
    writer_kws=writer_kws,
    reader_kws=reader_kws,
)


@pytest.mark.parametrize(
    "mesh_ref, file_format",
    [
        (helpers.tet_mesh, "avsucd"),
        (helpers.tet_mesh, "flac3d"),
        (helpers.tet_mesh, "pickle"),
        (helpers.tet_mesh, "tecplot"),
        (helpers.hex_mesh, "avsucd"),
        (helpers.hex_mesh, "flac3d"),
        (helpers.hex_mesh, "pickle"),
        (helpers.hex_mesh, "tecplot"),
        (helpers.hybrid_mesh, "avsucd"),
        (helpers.hybrid_mesh, "flac3d"),
        (helpers.hybrid_mesh, "pickle"),
    ],
)
def test_meshio(mesh_ref, file_format):
    mesh = write_read(
        mesh=mesh_ref,
        writer_kws={"file_format": file_format},
        reader_kws={"file_format": file_format},
    )

    helpers.allclose_mesh(mesh_ref, mesh)
