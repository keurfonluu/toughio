from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class NCGAS(DataBlock):
    name = "NCGAS"
    formats = {1: "5d", 2: "10s"}
    multiples = {2}

    def _read(
        self,
        f: FileIterator | TextIO | str,
    ) -> dict:
        """Read NCGAS block data."""
        ncgas = {"non_condensible_gas": []}
        
        # Record 1
        data = self.readers[1](f)
        n = data[0]

        # Record 2
        for _ in range(n):
            data = self.readers[2](f)
            ncgas["non_condensible_gas"].append(data[0])

        return ncgas

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write NCGAS block data."""
        data = parameters["non_condensible_gas"]

        # Record 1
        out = self.writers[1]([len(data)])

        # Record 2
        out += self.writers[2](data)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if NCGAS block should be written."""
        return len(parameters.get("non_condensible_gas", [])) > 0
