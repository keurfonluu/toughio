from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class POISE(DataBlock):
    name = "POISE"
    formats = {}

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read POISE block data."""
        poise = {"react": {"poiseuille": {}}}

        line = f.next().strip()
        data = [float(x) for x in line.split()]  # Free-format

        if len(data) < 5:
            raise ValueError()

        poise["react"]["poiseuille"]["start"] = data[:2]
        poise["react"]["poiseuille"]["end"] = data[2:4]
        poise["react"]["poiseuille"]["aperture"] = data[4]

        return poise

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write POISE block data."""
        poise = parameters["react"]["poiseuille"]

        for key in ["start", "end", "aperture"]:
            if key not in poise:
                raise ValueError()

            if key != "aperture" and len(poise[key]) != 2:
                raise ValueError()

        values = [x for x in poise["start"][:2]]
        values += [x for x in poise["end"][:2]]
        values += [poise["aperture"]]
        out = [f"{' '.join(str(x) for x in values)}\n"]

        return out

    def _write_conditions(
        self, parameters: dict, simulator: str, *args, **kwargs
    ) -> bool:
        """Check if POISE block should be written."""
        return (
            parameters.get("react", {}).get("poiseuille") and simulator == "toughreact"
        )

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a POISE block."""
        parameters.setdefault("react", {}).update(data["react"])
