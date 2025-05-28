from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class MOMOP(DataBlock):
    name = "MOMOP"
    formats = {1: ",".join(80 * ["1d"])}

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read MOMOP block data."""
        data = self.readers[1](f)
        momop = {"more_options": {i + 1: x for i, x in enumerate(data) if x is not None}}

        return momop

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write MOMOP block data."""
        values = [parameters["more_options"].get(k + 1) for k in range(80)]
        out = self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if MOMOP block should be written."""
        return bool(parameters.get("more_options", {}))
