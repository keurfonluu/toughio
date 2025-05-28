from __future__ import annotations

from .title import TITLE
from .dimen import DIMEN
from .rocks import ROCKS
from .rpcap import RPCAP
from .react import REACT
from .flac import FLAC
from .chemp import CHEMP
from .ncgas import NCGAS
from .multi import MULTI
from .solvr import SOLVR
from .index import INDEX
from .start import START
from .param import PARAM
from .selec import SELEC
from .indom import INDOM
from .momop import MOMOP
from .times import TIMES
from .hyste import HYSTE
from .oft import FOFT, COFT, GOFT
from .roft import ROFT
from .gener import GENER
from .timbc import TIMBC
from .diffu import DIFFU
from .outpt import OUTPT
from .outpu import OUTPU
from .eleme import ELEME
from .coord import COORD
from .conne import CONNE
from .incon import INCON
from .meshm import MESHM
from .poise import POISE
from .nover import NOVER
from .endcy import ENDCY
from .end_comments import END_COMMENTS

from .....core import DataBlock


registered_blocks = [
    (TITLE, 100),
    (DIMEN, 98),
    (ROCKS, 96),
    (RPCAP, 94),
    (REACT, 92),
    (FLAC, 90),
    (CHEMP, 88),
    (NCGAS, 86),
    (MULTI, 84),
    (SOLVR, 82),
    (INDEX, 80),
    (START, 78),
    (PARAM, 76),
    (SELEC, 74),
    (INDOM, 72),
    (MOMOP, 70),
    (TIMES, 68),
    (HYSTE, 66),
    (FOFT, 64),
    (COFT, 62),
    (GOFT, 60),
    (ROFT, 58),
    (GENER, 56),
    (TIMBC, 54),
    (DIFFU, 52),
    (OUTPT, 50),
    (OUTPU, 48),
    (ELEME, 46),
    (COORD, 44),
    (CONNE, 42),
    (INCON, 40),
    (MESHM, 38),
    (POISE, 36),
    (NOVER, 34),
    (ENDCY, 32),
    (END_COMMENTS, 30),
]


def register_block(block: DataBlock, priority: int | float) -> None:
    """
    Register a new block with a specified priority.

    Parameters
    ----------
    block : DataBlock
        The block class to register
    priority : scalar
        The priority of the block, higher values are processed first.
        
    """
    registered_blocks.append((block, priority))
