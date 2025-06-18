from ._json import read, write
from .._helpers import register

register("json", [".json"], read, write)
