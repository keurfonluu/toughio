from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class COORD(DataBlock):
    name = "COORD"
    formats = {1: ",".join(3 * ["20f"])}
    _space_between_blocks = True

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read COORD block data."""
        coord = []

        # Read records
        line = f.next()

        while True:
            if line.strip():
                data = self.readers[1](line)
                coord.append(data)

            else:
                break

            line = f.next()

        return coord

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write COORD block data."""
        out = []

        for v in parameters["elements"].values():
            out += self.writers[1](v["center"])

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if COORD block should be written."""
        return parameters.get("coordinates", False)

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a COORD block."""
        parameters["coordinates"] = True
