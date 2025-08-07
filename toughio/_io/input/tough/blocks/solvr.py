from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class SOLVR(DataBlock):
    name = "SOLVR"
    formats = {
        1: "1s,4S,5S,10f,10f,10d"}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        simulator: str,
        *args,
        **kwargs
    ) -> dict:
        """Read SOLVR block data."""
        solvr = {}

        # Read records
        line = f.next()
        data = self.readers[1](line)

        if simulator == "tough4" or "," in line:
            tmp = {
                "lib": int(data[0]) if data[0].isdigit() else data[0],
                "method": data[1],
                "precond": data[2],
                "eps": data[4],
                "n_iteration": data[5],
            }

        else:
            tmp = {
                "method": int(data[0]) if data[0].isdigit() else data[0],
                "z_precond": data[1],
                "o_precond": data[2],
                "rel_iter_max": data[3],
                "eps": data[4],
            }

        solvr["solver"] = self.prune_values(tmp)

        return solvr

    def _write(self, parameters: dict, simulator: str, *args, **kwargs) -> list[str]:
        """Write SOLVR block data."""
        if simulator == "tough4":
            values = [
                str(parameters["solver"].get("lib", "")),
                parameters["solver"].get("method"),
                parameters["solver"].get("precond"),
                None,
                parameters["solver"].get("eps"),
                parameters["solver"].get("n_iteration"),
            ]

        else:
            values = [
                str(parameters["solver"].get("method", "")),
                parameters["solver"].get("z_precond"),
                parameters["solver"].get("o_precond"),
                parameters["solver"].get("rel_iter_max"),
                parameters["solver"].get("eps"),
            ]

        out = self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if SOLVR block should be written."""
        return bool(parameters.get("solver", {}))
