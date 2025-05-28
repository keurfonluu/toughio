from __future__ import annotations

from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class SELEC(DataBlock):
    name = "SELEC"
    formats = {1: ",".join(16 * ["5d"]), 2: ",".join(8 * ["10f"])}

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read SELEC block data."""
        selec = {"selections": {}}

        # Read records
        data = self.readers[1](f)
        selec["selections"]["integers"] = {k + 1: v for k, v in enumerate(data)}

        if selec["selections"]["integers"][1]:
            selec["selections"]["floats"] = []

            for _ in range(selec["selections"]["integers"][1]):
                data = self.readers[2](f)
                selec["selections"]["floats"].append(self.prune_values(data))

        selec["selections"]["integers"] = self.prune_values(selec["selections"]["integers"])

        if selec["selections"]["integers"][1] == 1:
            selec["selections"]["floats"] = selec["selections"]["floats"][0]

        return selec

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write SELEC block data."""
        integers = parameters["selections"].get("integers", {})
        floats = parameters["selections"].get("floats")
        
        # Check floats and overwrite IE(1)
        if floats is not None and len(floats):
            if isinstance(floats[0], (list, tuple, np.ndarray)):
                for x in floats:
                    if len(x) > 8:
                        raise ValueError()

                integers[1] = len(floats)
                ndim = 2

            else:
                if len(floats) > 8:
                    raise ValueError()

                integers[1] = 1
                ndim = 1

        else:
            ndim = None

        # Record 1
        values = [integers[k] for k in sorted(integers)]
        out = self.writers[1](values)

        # Record 2
        if ndim == 1:
            out += self.writers[2](floats)

        elif ndim == 2:
            for x in floats:
                out += self.writers[2](x)

        else:
            out += self.writers[2]()

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if SELEC block should be written."""
        return bool(parameters.get("selections", {}))
