from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class NOVER(DataBlock):
    name = "NOVER"
    formats = {}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read NOVER block data."""
        return {"nover": True}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write NOVER block data."""
        return []

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if NOVER block should be written."""
        return parameters.get("nover", False)
