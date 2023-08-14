import os
import platform
import sys

import pytest

import toughio


@pytest.mark.parametrize(
    "exec, workers, docker, wsl, cmd",
    [
        ("tough-exec", None, None, False, "tough-exec INFILE INFILE.out"),
        ("tough-exec", 8, None, False, "mpiexec -n 8 tough-exec INFILE INFILE.out"),
    ],
)
def test_run(exec, workers, docker, wsl, cmd):
    status = toughio.run(
        exec,
        {},
        workers=workers,
        docker=docker,
        wsl=wsl,
        use_temp=sys.version_info
        >= (3, 8),  # dirs_exist_ok only works with Python > 3.8
        silent=True,
    )

    assert status.args == cmd


@pytest.mark.skipif(
    not platform.system().startswith("Win"), reason="requires Windows platform"
)
@pytest.mark.parametrize(
    "exec, workers, docker, wsl, cmd",
    [
        (
            "tough-exec",
            None,
            "docker-image",
            False,
            "docker run --rm  -v PLACEHOLDER:/shared -w /shared docker-image tough-exec INFILE INFILE.out",
        ),
        ("tough-exec", None, None, True, "bash -c 'tough-exec INFILE INFILE.out'"),
        (
            "tough-exec",
            8,
            "docker-image",
            True,
            """bash -c 'docker run --rm  -v PLACEHOLDER:/shared -w /shared docker-image mpiexec -n 8 tough-exec INFILE INFILE.out'""",
        ),
    ],
)
def test_run_windows(exec, workers, docker, wsl, cmd):
    if os.getenv("ComSpec").endswith("cmd.exe"):
        cmd = cmd.replace("PLACEHOLDER", '"%cd%"')

    else:
        cmd = cmd.replace("PLACEHOLDER", "${PWD}")

    test_run(exec, workers, docker, wsl, cmd)


@pytest.mark.skipif(
    platform.system().startswith("Win"), reason="requires Unix platform"
)
@pytest.mark.parametrize(
    "exec, workers, docker, cmd",
    [
        (
            "tough-exec",
            None,
            "docker-image",
            "docker run --rm PLACEHOLDER -v ${PWD}:/shared -w /shared docker-image tough-exec INFILE INFILE.out",
        ),
        (
            "tough-exec",
            8,
            "docker-image",
            "docker run --rm PLACEHOLDER -v ${PWD}:/shared -w /shared docker-image mpiexec -n 8 tough-exec INFILE INFILE.out",
        ),
    ],
)
def test_run_unix(exec, workers, docker, cmd):
    cmd = cmd.replace("PLACEHOLDER", f"-e LOCAL_USER_ID={os.getuid()}")
    test_run(exec, workers, docker, False, cmd)
