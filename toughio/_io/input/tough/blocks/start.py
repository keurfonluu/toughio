from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class START(DataBlock):
    name = "START"
    formats = {}

    def __init__(self, *args, **kwargs):
        """Initialize START block."""
        super().__init__(*args, **kwargs)
        self._space_between_blocks = False

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read START block data."""
        return {"start": True}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write START block data."""
        return []

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if START block should be written."""
        return parameters.get("start", False)
