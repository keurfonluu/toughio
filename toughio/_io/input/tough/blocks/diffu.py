from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class DIFFU(DataBlock):
    name = "DIFFU"
    formats = {1: ",".join(8 * ["10f"])}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read DIFFU block data."""
        diffu = {"diffusion": []}
        
        # Read records
        while True:
            i = f.tell()
            line = f.next()

            if line.split():
                try:
                    data = self.readers[1](line)
                    diffu["diffusion"].append(self.prune_values(data))

                except ValueError:
                    f.seek(i, increment=-1)
                    break

            else:
                break

        return diffu

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write DIFFU block data."""
        out = []

        for values in parameters["diffusion"]:
            out += self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if DIFFU block should be written."""
        return len(parameters.get("diffusion", [])) > 0
