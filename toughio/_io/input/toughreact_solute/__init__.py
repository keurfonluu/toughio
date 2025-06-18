from ._read import read
from ._write import write
from .._helpers import register

register("toughreact-solute", [], read, write)
