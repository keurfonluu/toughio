from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class OUTPT(DataBlock):
    name = "OUTPT"
    formats = {}

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read OUTPT block data."""
        outpt = {"react": {"output": {}}}

        line = f.next().strip()
        data = [int(x) for x in line.split()]  # Free-format

        if len(data):
            outpt["react"]["output"]["format"] = data[0]

        if len(data) > 1:
            outpt["react"]["output"]["shape"] = data[1:]

        return outpt

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write OUTPT block data."""
        outpt = parameters["react"]["output"]

        values = [outpt["format"]]
        values += outpt.get("shape", [])[:3]
        out = [f"{' '.join(str(x) for x in values)}\n"]

        return out

    def _write_conditions(self, parameters: dict, simulator: str, *args, **kwargs) -> bool:
        """Check if OUTPT block should be written."""
        return (
            parameters.get("react", {}).get("output", {}).get("format") is not None
            and simulator == "toughreact"
        )
