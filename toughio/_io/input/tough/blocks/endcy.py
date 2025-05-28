from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class ENDCY(DataBlock):
    name = "ENDCY"
    formats = {}

    def __init__(self, *args, **kwargs):
        """Initialize ENDCY block."""
        super().__init__(*args, **kwargs)
        self._space_between_blocks = False

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read ENDCY block data."""
        pass

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write ENDCY block data."""
        return []
