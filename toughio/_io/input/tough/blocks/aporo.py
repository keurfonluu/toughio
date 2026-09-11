from __future__ import annotations

from typing import TextIO
import numpy as np

from .....core import DataBlock, FileIterator


class APORO(DataBlock):
    name = "APORO"
    formats = {
        0: "5s,5d,10f,10f,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs,
    ) -> dict:
        """Read APORO block data."""
        aporo = {"rocks": {}}

        # Read records
        line = f.next()

        while True:
            if line.strip():
                data = self.readers[0](line)
                rock = data[0]
                phase = data[1]
                values = self.prune_values(data[2:])

                if all(value == values[0] for value in values):
                    values = values[0]

                tmp: dict = {"phase": phase} if phase else {}
                tmp["values"] = values
                aporo["rocks"].setdefault(rock, {"porosity_factor": []})["porosity_factor"].append(tmp)

            else:
                break

            line = f.next()

        return aporo

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write APORO block data."""
        out = []

        for k, v in parameters["rocks"].items():
            data = parameters.get("default", {}).copy()
            data.update(v)
            porosity_factors = data.get("porosity_factor", [])

            for factor in porosity_factors:
                factor_values = factor.get("values", [])
                factor_values = [factor_values] if np.ndim(factor_values) == 0 else factor_values
                values = [
                    k,
                    factor.get("phase"),
                    *factor_values,
                ]
                out += self.writers[0](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if APORO block should be written."""
        if "porosity_factor" in parameters.get("default", {}):
            return True

        for rock in parameters.get("rocks", {}).values():
            if "porosity_factor" in rock:
                if any(x is not None for x in rock["porosity_factor"]):
                    return True

        return False

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a APORO block."""
        for k, v in data["rocks"].items():
            parameters["rocks"][k].update(v)
