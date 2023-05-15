import glob
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
    docker=None,
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

    # Check if input file is in working directory, otherwise copy
    if not isinstance(input_filename, dict):
        input_path = pathlib.Path(input_filename)
        input_filename = working_dir / input_path.name

        if input_path.parent.absolute() != working_dir.absolute():
            shutil.copy(input_path, input_filename)

    else:
        write_input(working_dir / "INFILE", input_filename)
        input_filename = working_dir / "INFILE"

    # Copy other simulation files to working directory
    for k, v in other_filenames.items():
        filename = pathlib.Path(k)
        new_filename = pathlib.Path(v)

        if filename.parent.absolute() != working_dir.absolute() and filename.name != new_filename.name:
            shutil.copy(filename, working_dir / v)

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
        cwd=str(working_dir),
        **kwargs
    )

    # Clean up working directory
    filenames = glob.glob(f"{str(working_dir)}/*") + glob.glob(f"{str(working_dir)}/.*")

    for filename in filenames:
        for pattern in [".OUTPUT", "TABLE", "MESHA", "MESHB"]:
            if pathlib.Path(filename).name.startswith(pattern):
                os.remove(filename)

                break

    return status
