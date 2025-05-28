from __future__ import annotations

from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class OUTPU(DataBlock):
    name = "OUTPU"
    formats = {1: "20s", 2: "5d", 3: "20s,5d,5d"}
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read OUTPU block data."""
        outpu = {"output": {}}

        # Format
        data = self.readers[1](f)
        outpu["output"]["format"] = data[0] if data[0] else None

        # Variables
        data = self.readers[2](f)

        if data[0]:
            num_vars = data[0]
            outpu["output"]["variables"] = []

            for _ in range(num_vars):
                data = self.readers[3](f)
                name = data[0].lower()

                tmp = self.prune_values(data[1:])
                options = None if len(tmp) == 0 else tmp[0] if len(tmp) == 1 else tmp
                outpu["output"]["variables"].append({"name": name})

                if options is not None:
                    outpu["output"]["variables"][-1]["options"] = options

        return outpu

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write OUTPU block data."""
        out = []

        # Output format
        out += self.writers[1]([parameters["output"].get("format", "").upper()])

        # Variables
        if parameters["output"]["variables"]:
            buffer = []
            num_vars = len(parameters["output"].get("variables", []))

            for variable in parameters["output"].get("variables", []):
                values = [variable["name"].upper() if "name" in variable else None]
                v = variable.get("options")

                if v is not None:
                    if np.ndim(v) == 0:
                        values += [v]
                        buffer += self.writers[3](values)

                    else:
                        if np.ndim(v[0]) == 0:
                            values += list(v)
                            buffer += self.writers[3](values)

                        else:
                            for vv in v:
                                values_in = values + list(vv)
                                buffer += self.writers[3](values_in)

                else:
                    buffer += self.writers[3](values)

            out += self.writers[2]([num_vars])
            out += buffer

        return out

    def _write_conditions(self, parameters: dict, simulator: str, *args, **kwargs) -> bool:
        """Check if OUTPU block should be written."""
        outpu = False

        for key in ["format", "variables"]:
            if parameters.get("output", {}).get(key) is not None:
                outpu = True
            
        return outpu and simulator != "toughreact"
