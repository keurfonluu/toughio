from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class HYSTE(DataBlock):
    name = "HYSTE"
    formats = {1: ",".join(3 * ["5d"])}

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read HYSTE block data."""
        data = self.readers[1](f)
        hyste = {
            "hysteresis_options": {
                i + 1: x for i, x in enumerate(data) if x is not None
            }
        }

        return hyste

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write HYSTE block data."""
        values = [parameters["hysteresis_options"].get(k + 1) for k in range(3)]
        out = self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if HYSTE block should be written."""
        return bool(parameters.get("hysteresis_options", {}))
