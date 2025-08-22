from .chemp import CHEMP
from .conne import CONNE
from .coord import COORD
from .diffu import DIFFU
from .dimen import DIMEN
from .eleme import ELEME
from .end_comments import END_COMMENTS
from .endcy import ENDCY
from .flac import FLAC
from .gener import GENER
from .hyste import HYSTE
from .incon import INCON
from .index import INDEX
from .indom import INDOM
from .meshm import MESHM
from .modde import MODDE
from .momop import MOMOP
from .multi import MULTI
from .ncgas import NCGAS
from .nover import NOVER
from .oft import COFT, FOFT, GOFT
from .outpt import OUTPT
from .outpu import OUTPU
from .param import PARAM
from .poise import POISE
from .react import REACT
from .rocks import ROCKS
from .roft import ROFT
from .rpcap import RPCAP
from .selec import SELEC
from .solvr import SOLVR
from .start import START
from .timbc import TIMBC
from .times import TIMES
from .title import TITLE
from .wellb import WELLB


registered_blocks = [
    TITLE,
    DIMEN,
    ROCKS,
    RPCAP,
    MODDE,
    WELLB,
    REACT,
    FLAC,
    CHEMP,
    NCGAS,
    MULTI,
    SOLVR,
    INDEX,
    START,
    PARAM,
    SELEC,
    INDOM,
    MOMOP,
    TIMES,
    HYSTE,
    FOFT,
    COFT,
    GOFT,
    ROFT,
    GENER,
    TIMBC,
    DIFFU,
    OUTPT,
    OUTPU,
    ELEME,
    COORD,
    CONNE,
    INCON,
    MESHM,
    POISE,
    NOVER,
    ENDCY,
    END_COMMENTS,
]
