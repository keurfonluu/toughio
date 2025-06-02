from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class SOLVR(DataBlock):
    name = "SOLVR"
    formats = {1: "1s,4s,5s,10f,10f"}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read SOLVR block data."""
        solvr = {}

        # Read records
        data = self.readers[1](f)
        solvr["solver"] = {
            "method": int(data[0]) if data[0].isdigit() else data[0],
            "z_precond": data[1],
            "o_precond": data[2],
            "rel_iter_max": data[3],
            "eps": data[4],
        }
        solvr["solver"] = self.prune_values(solvr["solver"])

        return solvr

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write SOLVR block data."""
        values = [
            parameters["solver"].get(key) for key in [
                "method",
                "z_precond",
                "o_precond",
                "rel_iter_max",
                "eps",
            ]
        ]
        out = self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if SOLVR block should be written."""
        return bool(parameters.get("solver", {}))
