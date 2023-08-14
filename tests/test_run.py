import os
import platform

import pytest

import toughio


@pytest.mark.parametrize(
    "exec, workers, docker, wsl, cmd",
    [
        ("tough-exec", None, None, False, "tough-exec INFILE INFILE.out"),
        ("tough-exec", 8, None, False, "mpiexec -n 8 tough-exec INFILE INFILE.out"),
        (
            "tough-exec",
            None,
            "docker-image",
            False,
            "docker run --rm  -v PLACEHOLDER:/shared -w /shared docker-image tough-exec INFILE INFILE.out",
        ),
        ("tough-exec", None, None, True, 'bash -c "tough-exec INFILE INFILE.out"'),
        (
            "tough-exec",
            8,
            "docker-image",
            True,
            'bash -c "docker run --rm  -v PLACEHOLDER:/shared -w /shared docker-image mpiexec -n 8 tough-exec INFILE INFILE.out"',
        ),
    ],
)
def test_run(exec, workers, docker, wsl, cmd):
    status = toughio.run(
        exec,
        {},
        workers=workers,
        docker=docker,
        wsl=wsl,
        use_temp=True,
        silent=True,
    )

    if platform.system().startswith("Win") and os.getenv("ComSpec").endswith("cmd.exe"):
        cmd = cmd.replace("PLACEHOLDER", '"%cd%"')

    else:
        cmd = cmd.replace("PLACEHOLDER", "${PWD}")

    assert status.args == cmd
