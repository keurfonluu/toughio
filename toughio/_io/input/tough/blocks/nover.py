from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class NOVER(DataBlock):
    name = "NOVER"
    formats = {}

    def __init__(self, *args, **kwargs):
        """Initialize NOVER block."""
        super().__init__(*args, **kwargs)
        self._space_between_blocks = False

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read NOVER block data."""
        return {"nover": True}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write NOVER block data."""
        return []

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if NOVER block should be written."""
        return parameters.get("nover", False)
