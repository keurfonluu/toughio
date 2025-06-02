from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class INDEX(DataBlock):
    name = "INDEX"
    formats = {}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read INDEX block data."""
        return {"index": True}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write INDEX block data."""
        return []

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if INDEX block should be written."""
        return parameters.get("index", False)
