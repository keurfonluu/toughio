import os
import platform

import helpers
import pytest

import toughio


class FakePopen:
    """Record the command instead of executing it."""

    def __init__(self, args, **kwargs):
        self.args = args
        self.returncode = 0
        self.stdout = None
        self.pid = None

    def wait(self):
        return self.returncode


def run_command(monkeypatch, exec, workers, docker, wsl):
    """Return the shell command built by toughio.run without executing it."""
    monkeypatch.setattr(toughio._run, "_check_exec", False)
    monkeypatch.setattr(toughio._run.subprocess, "Popen", FakePopen)

    status = toughio.run(
        {},
        exec=exec,
        workers=workers,
        docker=docker,
        wsl=wsl,
        working_dir=helpers.tempdir(),
        use_temp=True,
        ignore_patterns=["INFILE"],
        silent=True,
        container_name="CONTAINER",
    )

    return status.args


# An executable given by name (i.e., found on PATH) is currently replaced by a
# quoted absolute path relative to the current working directory.
reason_run_1 = "executable on PATH is turned into a path in the working directory"


@pytest.mark.parametrize(
    "exec, workers, docker, wsl, cmd",
    [
        pytest.param(
            "tough-exec",
            None,
            None,
            False,
            "tough-exec INFILE INFILE.out",
            marks=pytest.mark.xfail(reason=reason_run_1, strict=True),
        ),
        pytest.param(
            "tough-exec",
            8,
            None,
            False,
            "mpiexec -n 8 tough-exec INFILE INFILE.out",
            marks=pytest.mark.xfail(reason=reason_run_1, strict=True),
        ),
    ],
)
def test_run(monkeypatch, exec, workers, docker, wsl, cmd):
    assert run_command(monkeypatch, exec, workers, docker, wsl) == cmd


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
            "docker run --name CONTAINER --rm --volume PLACEHOLDER:/shared --workdir /shared docker-image tough-exec INFILE INFILE.out",
        ),
        ("tough-exec", None, None, True, "bash -c 'tough-exec INFILE INFILE.out'"),
        (
            "tough-exec",
            8,
            "docker-image",
            True,
            """bash -c 'docker run --name CONTAINER --rm --volume PLACEHOLDER:/shared --workdir /shared docker-image mpiexec -n 8 tough-exec INFILE INFILE.out'""",
        ),
    ],
)
def test_run_windows(monkeypatch, exec, workers, docker, wsl, cmd):
    if os.getenv("ComSpec").endswith("cmd.exe"):
        cmd = cmd.replace("PLACEHOLDER", '"%cd%"')

    else:
        cmd = cmd.replace("PLACEHOLDER", "${PWD}")

    assert run_command(monkeypatch, exec, workers, docker, wsl) == cmd


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
            "docker run --name CONTAINER --rm --volume ${PWD}:/shared --workdir /shared docker-image tough-exec INFILE INFILE.out",
        ),
        (
            "tough-exec",
            8,
            "docker-image",
            "docker run --name CONTAINER --rm --volume ${PWD}:/shared --workdir /shared docker-image mpiexec -n 8 tough-exec INFILE INFILE.out",
        ),
    ],
)
def test_run_unix(monkeypatch, exec, workers, docker, cmd):
    cmd = cmd.replace("PLACEHOLDER", f"-e LOCAL_USER_ID={os.getuid()}")
    assert run_command(monkeypatch, exec, workers, docker, False) == cmd
