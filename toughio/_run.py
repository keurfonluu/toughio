import os
import pathlib
import shutil
import subprocess
import sys


def run(
    exec,
    input_filename,
    other_filenames=None,
    command=None,
    workers=None,
    wsl=False,
    working_dir=None,
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
    other_filenames : list of str or None, optional, default None
        Other simulation files to copy to working directory (e.g., MESH, INCON, GENER) if not already present.
    command : callable or None, optional, default None
        Command to execute TOUGH. Must be in the form ``f(exec, inp, out)``, where ``exec`` is the path to TOUGH executable, ``inp`` is the input file name, and ``out`` is the output file name.
    workers : int or None, optional, default None
        Number of MPI workers to invoke.
    wsl : bool, optional, default False
        Only for Windows. If `True`, run the final command as a Bash command.
    working_dir : str, pathlike or None, optional, default None
        Working directory. Input and output files will be generated in this directory.
    silent : bool, optional, default False
        If `True`, nothing will be printed to standard output.

    Returns
    -------
    :class:`subprocess.CompletedProcess`
        Subprocess completion status.
    
    """
    other_filenames = other_filenames if other_filenames else []
    if command is None:
        command = lambda exec, inp, out: f"{exec} {inp} {out}"

    # Executable
    exec = str(exec)
    exec = f"{os.path.expanduser('~')}/{exec[2:]}" if exec.startswith("~/") else exec

    # Working directory
    working_dir = os.getcwd() if working_dir is None else working_dir
    working_dir = pathlib.Path(working_dir)
    working_dir.mkdir(parents=True, exist_ok=True)

    # Check if input file is in working directory, otherwise copy
    input_path = pathlib.Path(input_filename)
    input_filename = working_dir / input_path.name

    if input_path.parent.absolute() != working_dir.absolute():
        shutil.copy(input_path, input_filename)

    # Copy other simulation files to working directory
    for filename in other_filenames:
        filename = pathlib.Path(filename)

        if filename.parent.absolute() != working_dir.absolute():
            shutil.copy(filename, working_dir)

    # Output filename
    output_filename = f"{input_filename.stem}.out"

    # TOUGH command
    cmd = command(exec, str(input_filename.name), str(output_filename))

    # Use MPI
    if workers is not None and workers > 1:
        cmd = f"mpiexec -n {workers} {cmd}"

    # Use WSL
    if wsl and sys.platform.startswith("win"):
        cmd = f'bash -c "{cmd}"'

    kwargs = {}
    if silent:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.STDOUT

    status = subprocess.run(
        cmd,
        shell=True,
        cwd=str(working_dir),
        **kwargs
    )

    return status
