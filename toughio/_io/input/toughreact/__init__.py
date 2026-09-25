from .chemical import (
    read as read_chemical,
    write as write_chemical,
)
from .flow import (
    read as read_flow,
    write as write_flow,
)
from .solute import (
    read as read_solute,
    write as write_solute,
)
from .._helpers import register


register("toughreact-chemical", [], read_chemical, write_chemical)
register("toughreact-flow", [], read_flow, write_flow)
register("toughreact-solute", [], read_solute, write_solute)
