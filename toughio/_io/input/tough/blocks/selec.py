from __future__ import annotations

import re
from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class SELEC(DataBlock):
    name = "SELEC"
    formats = {
        1: ",".join(16 * ["5d"]),
        2: ",".join(8 * ["10f"]),
    }
    _ie_pattern = re.compile(
        r"IE\((\d+)\)\s*=\s*(-?\d+)",
        re.IGNORECASE,
    )
    _fe_pattern = re.compile(
        r"^FE\((\d+)\)\s*=\s*(-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)",
        re.IGNORECASE,
    )

    def _parse_flexible_record(self, line: str, type_: str) -> tuple[int, int | float]:
        """Parse a flexible record line."""
        if type_ == "int":
            match = self._ie_pattern.match(line)
            i = int(match.group(1))
            v = int(match.group(2))

        else:
            match = self._fe_pattern.match(line)
            i = int(match.group(1))
            v = float(match.group(2))

        return i, v

    def _read(
        self, f: FileIterator | TextIO | str, simulator: str, *args, **kwargs
    ) -> dict:
        """Read SELEC block data."""
        from . import registered_blocks

        selec = {"selections": {}}

        # Read standard records
        i = f.tell()
        line = f.next(skip_empty=True, comments=("//", "!"))

        if not line.upper().startswith(("IE", "FE")):
            data = self.readers[1](line)

            selec["selections"]["integers"] = {
                k + 1: v for k, v in enumerate(data) if v is not None
            }

            if selec["selections"]["integers"].get(1, 0):
                selec["selections"]["floats"] = {}

                for i in range(selec["selections"]["integers"][1]):
                    data = self.readers[2](f)

                    for j, v in enumerate(data):
                        if v is not None:
                            selec["selections"]["floats"][i * 8 + j + 1] = v

        else:
            f.seek(i, increment=-1)

        # Read flexible records
        if simulator in {"tough", "tough4"}:
            registered_blocks = tuple([block.name for block in registered_blocks])

            while True:
                i = f.tell()
                line = f.next(skip_empty=True, comments=("//", "!"))

                if line.startswith(registered_blocks):
                    f.seek(i, increment=-1)
                    break

                if line.upper().startswith("IE"):
                    k, v = self._parse_flexible_record(line, "int")
                    selec["selections"].setdefault("integers", {})[k] = v

                elif line.upper().startswith("FE"):
                    k, v = self._parse_flexible_record(line, "float")
                    selec["selections"].setdefault("floats", {})[k] = v

        return selec

    def _write(self, parameters: dict, simulator: str, *args, **kwargs) -> list[str]:
        """Write SELEC block data."""
        out = []
        integers = parameters["selections"].get("integers", {})
        floats = parameters["selections"].get("floats", {})

        if simulator != "tough4":
            # Check floats and overwrite IE(1)
            IE1 = int(np.ceil(max(floats) / 8)) if floats else 0

            # Record 1
            values = [integers.get(k + 1) for k in range(16)]
            values[0] = IE1
            out += self.writers[1](values)

            # Record 2
            for i in range(IE1):
                values = [floats.get(i * 8 + k + 1) for k in range(8)]
                out += self.writers[2](values)

        else:
            # Keep old format for IE <= 16 and FE <= 8
            integers_old = {k: v for k, v in integers.items() if k <= 16}
            floats_old = {k: v for k, v in floats.items() if k <= 8}

            if floats_old:
                integers_old[1] = 1

            if integers_old:
                values = [integers_old.get(k + 1) for k in range(16)]
                out += self.writers[1](values)

                if floats_old:
                    values = [floats_old.get(k + 1) for k in range(8)]
                    out += self.writers[2](values)

            # New format for IE > 16 and FE > 8
            equal = " = " if self.space_between_values else "="
            out += [
                *[
                    f"IE({k}){equal}{v}\n"
                    for k, v in sorted(integers.items())
                    if k > 16
                ],
                *[f"FE({k}){equal}{v}\n" for k, v in sorted(floats.items()) if k > 8],
            ]

        return out

    def _write_header(self) -> str:
        """Write the header for the SELEC block."""
        return "SELEC----2----3----4----5----6----7----8----9---10---11---12---13---14---15---16\n"

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if SELEC block should be written."""
        return bool(parameters.get("selections", {}))
