import pathlib
from io import TextIOWrapper

from ..._common import filetype_from_filename, register_format


__all__ = [
    "register",
    "read",
    "write",
]


_extension_to_filetype = {}
_reader_map = {}
_writer_map = {}


def register(file_format, extensions, reader, writer=None):
    """
    Register a new input format.

    Parameters
    ----------
    file_format : str
        File format to register.
    extensions : array_like
        List of extensions to associate to the new format.
    reader : callable
        Read fumction.
    writer : callable or None, optional, default None
        Write function.

    """
    register_format(
        fmt=file_format,
        ext_to_fmt=_extension_to_filetype,
        reader_map=_reader_map,
        writer_map=_writer_map,
        extensions=extensions,
        reader=reader,
        writer=writer,
    )


def read(filename, file_format=None, **kwargs):
    """
    Read TOUGH input file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    file_format : str ('tough', 'toughreact-flow', 'toughreact-solute', 'toughreact-chemical', 'json') or None, optional, default None
        Input file format.

    Other Parameters
    ----------------
    blocks : list of str or None, optional, default None
        Only if ``file_format = "tough"``. Blocks to read. If None, all blocks are read.
    label_length : int or None, optional, default None
        Only if ``file_format = "tough"``. Number of characters in cell labels.
    n_variables : int or None, optional, default None
        Only if ``file_format = "tough"``. Number of primary variables.
    eos : str or None, optional, default None
        Only if ``file_format = "tough"``. Equation of State.
    mopr_11 : int, optional, default 0
        Only if ``file_format = "toughreact-solute"``. MOPR(11) value in file 'flow.inp'.

    Returns
    -------
    dict
        TOUGH input parameters.

    Note
    ----
    If ``file_format == 'tough'``, can also read `MESH`, `INCON` and `GENER` files.

    """
    file_format, simulator = _get_file_format_simulator(filename, file_format)

    return _reader_map[file_format](filename, simulator=simulator, **kwargs)


def write(filename, parameters, file_format=None, **kwargs):
    """
    Write TOUGH input file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    parameters : dict
        Parameters to export.
    file_format : str ('tough', 'toughreact-flow', 'toughreact-solute', 'toughreact-chemical', 'json') or None, optional, default None
        Output file format.

    Other Parameters
    ----------------
    block : str {'all', 'gener', 'mesh', 'incon'} or None, optional, default None
        Only if ``file_format = "tough"``. Blocks to be written:

         - 'all': write all blocks,
         - 'gener': only write block GENER,
         - 'mesh': only write blocks ELEME, COORD and CONNE,
         - 'incon': only write block INCON,
         - None: write all blocks except blocks defined in `ignore_blocks`.

    ignore_blocks : list of str or None, optional, default None
        Only if ``file_format = "tough"`` and `block` is None. Blocks to ignore.
    space_between_blocks : bool, optional, default False
        Only if ``file_format = "tough"``. Add an empty record between blocks.
    space_between_values : bool, optional, default True
        Only if ``file_format = "tough"``. Add a white space between floating point values.
    eos : str or None, optional, default None
        Only if ``file_format = "tough"``. Equation of State.
        If `eos` is defined in `parameters`, this option will be ignored.
    mopr_10 : int, optional, default 0
        Only if ``file_format = "toughreact-solute"``. MOPR(10) value in file 'flow.inp'.
    mopr_11 : int, optional, default 0
        Only if ``file_format = "toughreact-solute"``. MOPR(11) value in file 'flow.inp'.
    verbose : bool, optional, default True
        Only if ``file_format`` in {"toughreact-solute", "toughreact-chemical"}. If `True`, add comments to describe content of file.

    """
    file_format, simulator = _get_file_format_simulator(filename, file_format)
    _writer_map[file_format](filename, parameters, simulator=simulator, **kwargs)


def _get_file_format_simulator(filename, file_format, default="tough"):
    """Get file format."""
    if file_format in _file_format_to_simulator:
        return "tough", _file_format_to_simulator[file_format]

    if not file_format and not isinstance(filename, TextIOWrapper):
        filename = pathlib.Path(filename).name
        file_format = _filename_to_file_format.get(filename)

    if not file_format:
        file_format = filetype_from_filename(filename, _extension_to_filetype, default)

    if not file_format:
        file_format = "tough"

    return file_format, "tough"


_filename_to_file_format = {
    "INFILE": "tough",
    "MESH": "tough",
    "INCON": "tough",
    "GENER": "tough",
    "flow.inp": "toughreact-flow",
    "solute.inp": "toughreact-solute",
    "chemical.inp": "toughreact-chemical",
}

_file_format_to_simulator = {
    "tough": "tough",
    "toughreact-flow": "toughreact",
    "toughreact-solute": "toughreact",
    "toughreact-chemical": "toughreact",
    "tough3": "tough3",
    "tough4": "tough4",
}
