from ._read import read
from ._write import write
from .._helpers import register

for file_format in ("tough4", "tough3", "tough"):
    register(file_format, [""], read, write)
