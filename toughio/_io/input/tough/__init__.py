from ._read import read
from ._write import write
from .._helpers import register

for file_format in ("tough", "tough3", "tough4"):
    register(file_format, [""], read, write)
