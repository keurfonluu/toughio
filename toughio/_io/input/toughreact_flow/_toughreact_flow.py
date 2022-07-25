from .. import tough


def read(filename, eos=None):
    """
    Read TOUGHREACT flow input file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Input file name or buffer.
    eos : str or None, optional, default None
        Equation of State.

    Returns
    -------
    dict
        TOUGHREACT flow input parameters.

    """
    return tough.read(filename, label_length=5, eos=eos, simulator="toughreact")


def write(filename, parameters, block=None, ignore_blocks=None, eos=None):
    """
    Write TOUGHREACT flow input file.

    Parameters
    ----------
    filename : str, pathlike or buffer
        Output file name or buffer.
    parameters : dict
        Parameters to export.
    block : str {'all', 'gener', 'mesh', 'incon'} or None, optional, default None
        Blocks to be written:
         - 'all': write all blocks,
         - 'gener': only write block GENER,
         - 'mesh': only write blocks ELEME, COORD and CONNE,
         - 'incon': only write block INCON,
         - None: write all blocks except blocks defined in `ignore_blocks`.
    ignore_blocks : list of str or None, optional, default None
        Blocks to ignore. Only if `block` is None.
    eos : str or None, optional, default None
        Equation of State. If `eos` is defined in `parameters`, this option will be ignored.

    """
    return tough.write(
        filename, parameters, block, ignore_blocks, eos, simulator="toughreact"
    )
