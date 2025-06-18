from __future__ import annotations

import os
from typing import TextIO


def read(
    filename: str | os.PathLike | TextIO,
    *args,
    **kwargs
) -> dict:
    """
    Read TOUGHREACT flow input file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Input file name or buffer.
    *args, **kwargs
        Additional arguments passed to the TOUGH read function.

    Returns
    -------
    dict
        TOUGHREACT flow input parameters.

    """
    from ... import tough

    return tough.read(filename, *args, **kwargs)


def write(
    filename: str | os.PathLike | TextIO,
    parameters: dict,
    *args,
    **kwargs
) -> None:
    """
    Write TOUGHREACT flow input file.

    Parameters
    ----------
    filename : str | PathLike | TextIO
        Output file name or buffer.
    parameters : dict
        Parameters to export.
    *args, **kwargs
        Additional arguments passed to the TOUGH write function.

    """
    from ... import tough

    return tough.write(filename, parameters, *args, **kwargs)
