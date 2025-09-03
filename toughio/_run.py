from __future__ import annotations

import os
import pathlib
import platform
import re
import secrets
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable, Sequence
from typing import Literal, Optional

import numpy as np
import psutil
from tqdm import tqdm


_check_exec = True  # Bool to be monkeypatched in tests


def run(
    input_filename: str | os.PathLike | dict,
    other_filenames: Optional[Sequence[str | os.PathLike] | dict] = None,
    simulator: Optional[Literal["tough2", "tough3", "tough4", "toughreact"]] = None,
    exec: Optional[str | os.PathLike] = None,
    command: Optional[Callable] = None,
    workers: Optional[int | tuple[int, int]] = None,
    docker: Optional[str] = None,
    wsl: bool = False,
    working_dir: Optional[str | os.PathLike] = None,
    use_temp: bool = False,
    ignore_patterns: Optional[Sequence[str]] = None,
    silent: bool = False,
    petsc_args: Optional[Sequence[str]] = None,
    docker_args: Optional[Sequence[str]] = None,
    tough4_args: Optional[Sequence[str]] = None,
    container_name: Optional[str] = None,
    **kwargs,
) -> subprocess.CompletedProcess:
    """
    Run TOUGH executable.

    Parameters
    ----------
    input_filename : str | PathLike | dict
        TOUGH input file name.
    other_filenames : Sequence[str | PathLike] | dict, optional
        Other simulation files to copy to working directory (e.g., MESH, INCON, GENER)
        if not already present. If *other_filenames* is a dict, must be in the form
        ``{new: old}``, where ``old`` is the current name of the file to copy, and
        ``new`` is the name of the file copied.
    simulator : {'tough2', 'tough3', 'tough4'}, default 'tough3'
        TOUGH simulator to use.
    exec : str | PathLike, optional
        Path to TOUGH executable. If None, use the environment variable:

         - TOUGH4: TOUGHIO_TOUGH4_EXEC

    command : Callable, optional
        Command to execute TOUGH. Must be in the form ``f(exec, inp, [out])``, where
        ``exec`` is the path to TOUGH executable, ``inp`` is the input file name, and
        ``out`` is the output file name (optional). Ignored if *simulator* is specified.
    workers : int | tuple[int, int], optional
        Number of MPI workers and/or OpenMP threads to invoke. If *workers* is an
        integer and *simulator* is 'tough4', *workers* is the number of OpenMP threads.
    docker : str, optional
        Name of Docker image.
    wsl : bool, default False
        Only for Windows. If `True`, run the final command as a Bash command.
    working_dir : str | PathLike, optional
        Working directory. Input and output files will be generated in this directory.
    use_temp : bool, default False
        If `True`, run simulation in a temporary directory, and copy simulation files
        to *working_dir* at the end of the simulation. This option may be required when
        running TOUGH through a Docker.
    ignore_patterns : Sequence[str], optional
        If provided, output files that match the glob-style patterns will be discarded.
    silent : bool, default False
        If `True`, nothing will be printed to standard output.
    petsc_args : Sequence[str], optional
        List of arguments passed to PETSc solver (written to `.petscrc`).
    docker_args : Sequence[str], optional
        List of arguments passed to `docker run` command.
    tough4_args : Sequence[str], optional
        List of arguments passed to TOUGH4 command.
    container_name : str, optional
        Name of Docker container.
    **kwargs
        Additional keyword arguments. See `toughio.write_input` for details.

    Returns
    -------
    subprocess.CompletedProcess
        Subprocess completion status.

    """
    from . import read_input, write_input

    simulator = simulator if simulator else "tough3"
    exec = exec if exec else os.getenv(f"TOUGHIO_{simulator.upper()}_EXEC")

    if not exec:
        raise ValueError(f"executable for {simulator} not specified")

    # Additional files required for simulation
    other_filenames = (
        {k: k for k in other_filenames}
        if isinstance(other_filenames, Sequence)
        else other_filenames
        if other_filenames
        else {}
    )

    ignore_patterns = list(ignore_patterns) if ignore_patterns else []
    ignore_patterns += [".OUTPUT*", "TABLE", "MESHA", "MESHB"]

    # Executable
    exec = str(exec)
    exec = f"{os.path.expanduser('~')}/{exec[2:]}" if exec.startswith("~/") else exec

    if _check_exec:
        if not docker:
            if shutil.which(exec) is None:
                raise RuntimeError(f"executable '{exec}' not found.")

        else:
            # Check if Docker is in the PATH
            if shutil.which("docker") is None:
                raise RuntimeError("Docker executable not found.")

            # Check if Docker daemon is running
            status = subprocess.run(
                ["docker", "version"],
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )

            if "Server" not in status.stdout:
                raise RuntimeError(
                    "cannot connect to the Docker daemon. Is the Docker daemon running?"
                )

            # Check if Docker image exists
            status = subprocess.run(
                ["docker", "images", "-q", docker],
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )

            if not status.stdout:
                raise RuntimeError(f"image '{docker}' not found.")

            # Check if the executable exists inside the image
            status = subprocess.run(
                ["docker", "run", "--rm", docker, "which", exec],
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )

            if not status.stdout:
                raise RuntimeError(
                    f"executable '{exec}' not found in Docker image '{docker}'."
                )

    # Working directory
    working_dir = os.getcwd() if working_dir is None else working_dir
    working_dir = pathlib.Path(working_dir)
    working_dir.mkdir(parents=True, exist_ok=True)

    # Simulation directory
    if use_temp:
        temp_dir = tempfile.mkdtemp()
        simulation_dir = pathlib.Path(temp_dir)

        with open(working_dir / "tempdir.txt", "w") as f:
            f.write(temp_dir)

    else:
        simulation_dir = working_dir

    # Check if input file is in simulation directory, otherwise copy
    if not isinstance(input_filename, dict):
        input_path = pathlib.Path(input_filename)
        input_filename = simulation_dir / input_path.name

        if input_path.parent.resolve() != simulation_dir.resolve():
            shutil.copy(input_path, input_filename)

    else:
        write_input(
            simulation_dir / "INFILE", input_filename, file_format=simulator, **kwargs
        )
        input_filename = simulation_dir / "INFILE"

    # Copy other simulation files to working directory
    for k, v in other_filenames.items():
        filename = pathlib.Path(v)
        new_filename = pathlib.Path(k)

        if (
            filename.parent.resolve() != simulation_dir.resolve()
            or filename.name != new_filename.name
        ):
            shutil.copy(filename, simulation_dir / new_filename.name)

    # PETSc arguments
    petsc_args = petsc_args if petsc_args else []

    if petsc_args:
        with open(simulation_dir / ".petscrc", "w") as f:
            for arg in petsc_args:
                if arg.startswith("-"):
                    f.write(f"{arg} ")

                else:
                    f.write(f"{arg}\n")

    # Output filename
    output_filename = f"{input_filename.stem}.out"

    # MPI/OpenMP workers
    n_mpi, n_omp = None, None

    if workers is not None:
        if np.ndim(workers) == 0:
            if simulator == "tough4":
                n_omp = workers

            else:
                n_mpi = workers

        else:
            n_omp, n_mpi = workers[:2]

    # TOUGH command
    if not docker and not wsl:
        exec = f'"{pathlib.Path(exec).absolute()}"'

    if simulator in {"tough2", "toughreact"}:
        cmd = f"{exec} < {input_filename.name} > {output_filename}"

    elif simulator == "tough3":
        cmd = f"{exec} {input_filename.name} {output_filename}"

    elif simulator == "tough4":
        cmd = f"{exec} -f {input_filename.name}"
        tough4_args = tough4_args if tough4_args else []

        # Use OpenMP
        if n_omp:
            try:
                i = tough4_args.index("-t")
                tough4_args[i + 1] = n_omp

            except ValueError:
                tough4_args += ["-t", n_omp]

        if tough4_args:
            cmd = f"{cmd} {' '.join(map(str, tough4_args))}"

    else:
        cmd = command(exec, str(input_filename.name), str(output_filename))

    # Use MPI
    if n_mpi:
        cmd = f"mpiexec -n {n_mpi} {cmd}"

    # Use Docker
    is_windows = platform.system().startswith("Win")

    if docker:
        container_name = (
            container_name if container_name else f"toughio_{secrets.token_hex(4)}"
        )

        if is_windows and os.getenv("ComSpec").endswith("cmd.exe"):
            cwd = '"%cd%"'

        else:
            cwd = "${PWD}"

        docker_args = list(docker_args) if docker_args else []
        docker_args += [
            "--name",
            container_name,
            "--rm",
            # Sometime raises a duplicate mount point error, use old-school volume instead (but shell must be True in this case)
            # "--mount",
            # f"type=bind,source={simulation_dir},target=/shared",
            "--volume",
            f"{cwd}:/shared",
            "--workdir",
            "/shared",
        ]
        cmd = f"docker run {' '.join(map(str, docker_args))} {docker} {cmd}"

    # Use WSL
    if wsl and is_windows:
        cmd = f"bash -c '{cmd}'"

    # Progress bar
    if not silent and simulator == "tough4":
        log_filename = simulation_dir / "TMsimulation.log"

        # Read useful variables
        parameters = read_input(input_filename, blocks=["PARAM"])
        t_ini = parameters.get("options", {}).get("t_ini", 0.0)
        t_max = parameters.get("options", {}).get("t_max")

        # Read t_ini from SAVE file
        save_filename = other_filenames.get("INCON")

        if save_filename:
            if pathlib.Path(save_filename).name.startswith("SAVE"):
                with open(save_filename) as f:
                    for line in f:
                        if line.startswith(("+++", ":::")):
                            break

                    end_comments = list(f)

                for comment in end_comments:
                    line = comment.strip().split()

                    if line[0].startswith("time_to_this_point"):
                        t_ini = float(line[-1].replace(",", ""))
                        break

        # Delete log file if it exists
        log_filename.unlink(missing_ok=True)

        # Start thread to monitor log file
        stop_event = threading.Event()
        monitor_thread = threading.Thread(
            target=display_progress_bar,
            args=(log_filename, stop_event, simulator, t_ini, t_max),
            daemon=True,
        )
        monitor_thread.start()

    # Run simulation
    try:
        # See <https://www.koldfront.dk/making_subprocesspopen_in_python_3_play_nice_with_elaborate_output_1594>
        p = subprocess.Popen(
            cmd,
            shell=True,  # shell must be True as the command may contain quotes
            cwd=str(simulation_dir),
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            universal_newlines=False,
        )

        stdout = []
        cr = False

        for line in open(os.dup(p.stdout.fileno()), newline=""):
            # Handle carriage return
            # newline in open is converting \r\n as \r moving \r at the end of the previous string
            # This is only an issue for Spyder
            line = f"\r{line}" if cr else line
            cr = line.endswith("\r")
            line = line[:-2] if cr else line

            if not silent and simulator != "tough4":
                print(line, end="", flush=True)
                stdout.append(line)

    except (KeyboardInterrupt, Exception) as e:
        # Stop Docker container
        if docker:
            status = subprocess.run(
                ["docker", "stop", container_name],
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )

        # Handle children process termination
        # See <https://stackoverflow.com/a/25134985/9729313>
        try:
            proc = psutil.Process(p.pid)
            for child_process in proc.children():
                child_process.send_signal(signal.SIGTERM)

            proc.send_signal(signal.SIGTERM)

        except psutil.NoSuchProcess:
            pass

        raise e

    p.wait()
    status = subprocess.CompletedProcess(
        args=p.args,
        returncode=p.returncode,
        stdout="".join(stdout),
    )

    if not silent and simulator == "tough4":
        stop_event.set()
        monitor_thread.join()

    # Move files from temporary directory and delete it
    if use_temp:
        for filename in simulation_dir.rglob("*"):
            match_pattern = False

            for pattern in ignore_patterns:
                if filename.match(pattern):
                    match_pattern = True
                    break

            if not match_pattern:
                move_file(filename, working_dir)

        shutil.rmtree(simulation_dir, ignore_errors=True)
        os.remove(working_dir / "tempdir.txt")

    return status


def display_progress_bar(
    filename: str | os.PathLike,
    stop_event: threading.Event,
    simulator: Optional[Literal["tough2", "tough3", "tough4", "toughreact"]] = None,
    t_ini: Optional[float] = None,
    t_max: Optional[float] = None,
) -> None:
    """Display a progress bar."""
    file = None
    simulator = simulator if simulator else "tough"
    message = f"Starting {simulator.upper()} simulation"
    pattern1 = re.compile(
        r"At\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]:\s*TimeStep\s*=\s*([+-]?\d*\.?\d+E[+-]?\d+|\d+)\s*MAX\{Residual\}\s*=\s*([+-]?\d*\.?\d+E[+-]?\d+|\d+)",
        re.IGNORECASE,
    )
    pattern2 = re.compile(
        r"\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*ST\s*=\s*([+-]?\d*\.?\d+E[+-]?\d+|\d+)\s*DT\s*=\s*([+-]?\d*\.?\d+E[+-]?\d+|\d+)",
        re.IGNORECASE,
    )

    with tqdm(initial=t_ini, total=t_max, bar_format=f"{message}...") as pbar:
        l_bar = "{desc}: {percentage:3.0f}%|"
        total = pretty_time(pbar.total) if pbar.total else "end"

        try:
            while not stop_event.is_set():
                if file is None:
                    try:
                        file = open(filename, "r")

                    except FileNotFoundError:
                        time.sleep(0.01)
                        continue

                where = file.tell()
                line = file.readline()

                if not line:
                    time.sleep(0.01)
                    file.seek(where)

                else:
                    if line.strip().startswith("...ITERATING"):
                        match = pattern1.search(line)

                        if match:
                            it = int(match.group(1))
                            itr = int(match.group(2))
                            dt = float(match.group(3))
                            dt_update = 0.0

                    else:
                        match2 = pattern2.search(line)

                        if match2:
                            it = int(match2.group(1))
                            itr = int(match2.group(2))
                            dt = float(match2.group(4))
                            dt_update = dt

                        else:
                            continue

                    n = pretty_time(pbar.n + dt_update)
                    r_bar = f"| {n}/{total} [it={it}({itr}), dt={pretty_time(dt)}] ({{elapsed}})"
                    pbar.bar_format = f"{l_bar}{{bar}}{r_bar}"
                    pbar.update(min(dt_update, pbar.total - pbar.n))

        finally:
            if file is not None:
                file.close()

        pbar.bar_format = f"End of {simulator.upper()} simulation at t={pretty_time(pbar.n)} ({{elapsed}})"
        pbar.update(0.0)


def pretty_time(seconds: float) -> str:
    """
    Convert seconds to a human-readable format.

    Parameters
    ----------
    seconds : float
        Time in seconds.

    Returns
    -------
    str
        Human-readable time string.

    """
    if seconds < 3600.0:
        return f"{seconds:.2f} sec"

    elif seconds < 86400.0:
        return f"{seconds / 3600.0:.2f} hr"

    elif seconds < 31557600.0:
        return f"{seconds / 86400.0:.2f} day"

    else:
        return f"{seconds / 31557600.0:.2f} yr"


def move_file(filename: str | os.PathLike, directory: str | os.PathLike) -> None:
    """Move a file and delete if it already exists in target directory."""
    filename = pathlib.Path(filename)
    directory = pathlib.Path(directory)
    target = directory / filename.name

    if target.is_file():
        os.remove(target)

    shutil.move(filename, target)
