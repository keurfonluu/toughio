from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class MULTI(DataBlock):
    name = "MULTI"
    formats = {1: ",".join(5 * ["5d"])}

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read MULTI block data."""
        multi = {}

        data = self.readers[1](f)
        multi["n_component"] = data[0]
        multi["isothermal"] = data[1] == data[0]
        multi["n_phase"] = data[2]
        multi["do_diffusion"] = data[3] == 8

        if len(data) > 4:
            multi["n_component_incon"] = data[4]

        multi["n_variables"] = multi["n_component"] + int(not multi["isothermal"])

        return multi

    def _write(self, parameters: dict, eos: str, *args, **kwargs) -> list[str]:
        """Write MULTI block data."""
        if eos == "tmvoc":
            for key in {"n_component", "n_phase"}:
                if parameters.get(key) is None:
                    raise ValueError(
                        "for 'tmvoc', at least 'n_component' and 'n_phase' must be specified"
                    )

        values = eos_values.get(eos, [0, 0, 0, 6]).copy()
        values[0] = parameters.get("n_component", values[0])
        values[1] = values[0] + int(not parameters.get("isothermal", False))
        values[2] = parameters.get("n_phase", values[2])

        # Handle diffusion
        if parameters.get("do_diffusion", False):
            values[3] = 8
            parameters["n_phase"] = values[2]  # Save for later check

        # Number of mass components
        if parameters.get("n_component_incon"):
            values.append(parameters["n_component_incon"])

        out = self.writers[1](values)

        return out

    def _write_conditions(
        self, parameters: dict, eos: str, simulator: str, *args, **kwargs
    ) -> bool:
        """Check if MULTI block should be written."""
        return (
            parameters.get("eos", eos)
            or parameters.get("n_component")
            or parameters.get("n_phase")
            or parameters.get("n_component_incon")
        ) and not (bool(parameters.get("eos")) and simulator == "tough4")


eos_values = {
    "eos1": [1, 2, 2, 6],
    "eos2": [2, 3, 2, 6],
    "eos3": [2, 3, 2, 6],
    "eos4": [2, 3, 2, 6],
    "eos5": [2, 3, 2, 6],
    "eos7": [3, 3, 2, 6],
    "eos8": [3, 3, 3, 6],
    "eos9": [1, 1, 1, 6],
    "ewasg": [3, 4, 3, 6],
    "eco2n": [3, 4, 3, 6],
    "eco2n_v2": [3, 4, 3, 6],
    "eco2m": [3, 4, 4, 6],
    "tmvoc": [0, 0, 0, 6],
}
