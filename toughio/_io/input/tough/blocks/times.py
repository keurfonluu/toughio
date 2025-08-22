from __future__ import annotations

from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class TIMES(DataBlock):
    name = "TIMES"
    formats = {
        1: "5d,5d,10f,10f",
        "2/fixed": ",".join(8 * ["10f"]),
        "2/free": ",".join(20 * ["10f"]),
    }
    multiples = {"2/fixed", "2/free"}

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read TIMES block data."""
        times = {"times": []}

        # Record 1
        data = self.readers[1](f)
        n_times = data[0]

        # Record 2
        while len(times["times"]) < n_times:
            line = f.next()
            key = "2/free" if self.free_format or "," in line else "2/fixed"
            data = self.readers[key](line)
            times["times"] += self.prune_values(data)

        return times

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write TIMES block data."""
        data = parameters["times"]
        data = data if np.ndim(data) else [data]

        # Record 1
        out = self.writers[1]([len(data)])

        # Record 2
        key = "2/free" if self.free_format else "2/fixed"
        out += self.writers[key](data)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if TIMES block should be written."""
        return len(parameters.get("times", [])) > 0
