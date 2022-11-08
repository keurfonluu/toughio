import copy

import helpers
import pytest

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
    "mesh_ref, file_format, binary",
    [
        (helpers.tet_mesh, "avsucd", None),
        (helpers.tet_mesh, "flac3d", False),
        (helpers.tet_mesh, "flac3d", True),
        (helpers.tet_mesh, "pickle", None),
        (helpers.tet_mesh, "tecplot", None),
        (helpers.hex_mesh, "avsucd", None),
        (helpers.hex_mesh, "flac3d", False),
        (helpers.hex_mesh, "flac3d", True),
        (helpers.hex_mesh, "pickle", None),
        (helpers.hex_mesh, "tecplot", None),
        (helpers.hybrid_mesh, "avsucd", None),
        (helpers.hybrid_mesh, "flac3d", False),
        (helpers.hybrid_mesh, "flac3d", True),
        (helpers.hybrid_mesh, "pickle", None),
    ],
)
def test_meshio(mesh_ref, file_format, binary):
    mesh_ref = copy.deepcopy(mesh_ref)
    writer_kws = {"file_format": file_format}
    if binary is not None:
        writer_kws["binary"] = binary

    mesh = write_read(
        mesh=mesh_ref,
        writer_kws=writer_kws,
        reader_kws={"file_format": file_format},
    )

    # Some meshes do not support point and/or cell data
    helpers.allclose(mesh, mesh_ref)
