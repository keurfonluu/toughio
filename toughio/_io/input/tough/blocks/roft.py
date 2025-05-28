from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class ROFT(DataBlock):
    name = "ROFT"
    formats = {1: "5s,5s"}
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read ROFT block data."""
        history = {"rock_history": []}

        # Read records
        line = f.next()

        while True:
            if line.strip():
                data = self.readers[1](line)
                rock1 = data[0] if data[0] else ""
                rock2 = data[1] if data[1] else ""
                history["rock_history"].append([rock1, rock2])

            else:
                break

            line = f.next()

        return history

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write ROFT block data."""
        out = []

        for values in parameters["rock_history"]:
            out += self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if ROFT block should be written."""
        return len(parameters.get("rock_history", {})) > 0
