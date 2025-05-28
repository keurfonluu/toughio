from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class SOLVR(DataBlock):
    name = "SOLVR"
    formats = {1: "1d,2s,2s,3s,2s,10f,10f"}

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read SOLVR block data."""
        solvr = {}

        # Read records
        data = self.readers[1](f)
        solvr["solver"] = {
            "method": data[0],
            "z_precond": data[2],
            "o_precond": data[4],
            "rel_iter_max": data[5],
            "eps": data[6],
        }

        return solvr

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write SOLVR block data."""
        values = [
            parameters["solver"].get(key) for key in [
                "method",
                "__EMPTY__",
                "z_precond",
                "__EMPTY__",
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
