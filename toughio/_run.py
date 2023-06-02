import glob
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def run(
    exec,
    input_filename,
    other_filenames=None,
    command=None,
    workers=None,
    docker=None,
    wsl=False,
    working_dir=None,
    use_temp=False,
    silent=False
):
    """
    Run TOUGH executable.

    Parameters
    ----------
    exec : str or pathlike
        Path to TOUGH executable.
    input_filename : str or pathlike
        TOUGH input file name.
    other_filenames : list, dict or None, optional, default None
        Other simulation files to copy to working directory (e.g., MESH, INCON, GENER) if not already present. If ``other_filenames`` is a dict, must be in the for ``{old: new}``, where ``old`` is the current name of the file to copy, and ``new`` is the name of the file copied.
    command : callable or None, optional, default None
        Command to execute TOUGH. Must be in the form ``f(exec, inp, [out])``, where ``exec`` is the path to TOUGH executable, ``inp`` is the input file name, and ``out`` is the output file name (optional).
    workers : int or None, optional, default None
        Number of MPI workers to invoke.
    docker : str, optional, default None
        Name of Docker image.
    wsl : bool, optional, default False
        Only for Windows. If `True`, run the final command as a Bash command. Ignored if `docker` is not None.
    working_dir : str, pathlike or None, optional, default None
        Working directory. Input and output files will be generated in this directory.
    use_temp : bool, optional, default False
        If `True`, run simulation in a temporary directory, and copy simulation files to `working_dir` at the end of the simulation.
    silent : bool, optional, default False
        If `True`, nothing will be printed to standard output.

    Returns
    -------
    :class:`subprocess.CompletedProcess`
        Subprocess completion status.
    
    """
    from . import write_input

    other_filenames = (
        {k: k for k in other_filenames}
        if isinstance(other_filenames, (list, tuple))
        else other_filenames
        if other_filenames
        else {}
    )

    if command is None:
        command = lambda exec, inp, out: f"{exec} {inp} {out}"

    # Executable
    exec = str(exec)
    exec = f"{os.path.expanduser('~')}/{exec[2:]}" if exec.startswith("~/") else exec

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

        if input_path.parent.absolute() != simulation_dir.absolute():
            shutil.copy(input_path, input_filename)

    else:
        write_input(simulation_dir / "INFILE", input_filename)
        input_filename = simulation_dir / "INFILE"

    # Copy other simulation files to working directory
    for k, v in other_filenames.items():
        filename = pathlib.Path(k)
        new_filename = pathlib.Path(v)

        if filename.parent.absolute() != simulation_dir.absolute() or filename.name != new_filename.name:
            shutil.copy(filename, simulation_dir / v)

    # Output filename
    output_filename = f"{input_filename.stem}.out"

    # TOUGH command
    cmd = command(exec, str(input_filename.name), str(output_filename))

    # Use MPI
    if workers is not None and workers > 1:
        cmd = f"mpiexec -n {workers} {cmd}"

    # Use Docker or WSL
    platform = sys.platform

    if docker:
        if platform.startswith("win") and os.getenv("ComSpec").endswith("cmd.exe"):
            cwd = "%cd%"

        else:
            cwd = "${PWD}"

        cmd = f"docker run -it --rm -v {cwd}:/work -w /work {docker} {cmd}"

    elif wsl and platform.startswith("win"):
        cmd = f'bash -c "{cmd}"'

    kwargs = {}
    if silent:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.STDOUT

    status = subprocess.run(
        cmd,
        shell=True,
        cwd=str(simulation_dir),
        **kwargs
    )

    # List of files to delete
    patterns = [".OUTPUT", "TABLE", "MESHA", "MESHB"]

    # Copy files from temporary directory and delete it
    if use_temp:
        for filename in glob.glob(f"{str(simulation_dir)}/*"):
            flag = True
            
            for pattern in patterns:
                if pathlib.Path(filename).name.startswith(pattern):
                    flag = False
                    break
            
            if flag:
                shutil.copy(filename, working_dir)

        shutil.rmtree(simulation_dir, ignore_errors=True)

    # Clean up working directory
    filenames = glob.glob(f"{str(working_dir)}/*") + glob.glob(f"{str(working_dir)}/.*")

    for filename in filenames:
        for pattern in patterns + ["tempdir.txt"]:
            if pathlib.Path(filename).name.startswith(pattern):
                os.remove(filename)

                break

    return status
