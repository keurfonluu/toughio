from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class REACT(DataBlock):
    name = "REACT"
    formats = {1: "25d"}

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read REACT block data."""
        data = self.readers[1](f)
        react = {"react": {"options": {i + 1: x for i, x in enumerate(data) if x is not None}}}

        return react

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write REACT block data."""
        values = [parameters["react"]["options"].get(k + 1) for k in range(25)]
        out = self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, simulator: str, *args, **kwargs) -> bool:
        """Check if REACT block should be written."""
        return (
            bool(parameters.get("react", {}).get("options", {}))
            and simulator == "toughreact"
        )
