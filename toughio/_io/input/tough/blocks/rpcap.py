from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class RPCAP(DataBlock):
    name = "RPCAP"
    formats = {
        1: "5d,5s,10f,10f,10f,10f,10f,10f,10f",
        2: "5d,10f,10f,10f,10f,10f,10f,10f",  # Free format
    }

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read RPCAP block data."""
        rpcap = {}

        for key in ["relative_permeability", "capillarity"]:
            line = f.next()

            if self.free_format or "," in line:
                rpcap[key] = self.read_model_record(line, self.readers[2], 1)

            else:
                rpcap[key] = self.read_model_record(line, self.readers[1], 2)

        return rpcap

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write RPCAP block data."""
        out = []
        model_writer = self.writers[2] if self.free_format else self.writers[1]

        for key in ["relative_permeability", "capillarity"]:
            if key in parameters["default"]:
                out += self.write_model_record(parameters["default"], key, model_writer)

            else:
                out += self.writers[1]()

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if RPCAP block should be written."""
        return (
            parameters.get("default", {}).get("relative_permeability", {}).get("id")
            is not None
            or parameters.get("default", {}).get("capillarity", {}).get("id")
            is not None
        )

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a RPCAP block."""
        parameters.setdefault("default", {}).update(data)
