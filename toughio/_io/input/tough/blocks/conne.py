from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import Any, TextIO

from .....core import DataBlock, FileIterator


class CONNE(DataBlock):
    name = "CONNE"
    formats = {
        5: "5s,5s,5d,5d,5d,5d,10f,10f,10f,10f,10f",
        6: "6s,6s,5d,4d,4d,5d,10f,10f,10f,10f,10f",
        7: "7s,7s,5d,3d,3d,5d,10f,10f,10f,10f,10f",
        8: "8s,8s,3d,3d,3d,5d,10f,10f,10f,10f,10f",
        9: "9s,9s,3d,2d,2d,5d,10f,10f,10f,10f,10f",
        "5/tough4-free": "5s,5s,5d,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        simulator: str,
        *args,
        **kwargs
    ) -> dict:
        """Read CONNE block data."""
        conne = {"connections": {}}

        # Label length
        line = f.next()

        if not label_length:
            label_length = self.get_label_length(line[:9])

        label_format = f"{{:>{2 * label_length}}}"

        # Read records
        flag = False

        if simulator == "tough4":
            if self.free_format:
                read_record = self._read_record_tough4_free

            else:
                read_record = partial(self._read_record_default, label_length=5)

        else:
            read_record = partial(self._read_record_default, label_length=label_length)

        while True:
            if line.strip() and not line.startswith(("+++", ":::")):
                l1, l2, tmp = read_record(line)
                label = label_format.format(f"{l1}{l2}")
                conne["connections"][label] = self.prune_values(tmp)

            else:
                flag = line.startswith("+++")
                break

            try:
                line = f.next()

            except StopIteration:
                break

        return {
            "data": conne,
            "flag": flag,
            "label_length": label_length,
        }

    def _read_record_tough4_free(self, line: str) -> tuple[str, str, dict]:
        """Read a record in free format for TOUGH4."""
        data = self.readers["5/tough4-free"](line)

        return data[0], data[1], {
            "permeability_direction": data[2],
            "nodal_distances": data[3:5],
            "interface_area": data[5],
            "gravity_cosine_angle": data[6],
            "radiant_emittance_factor": data[7],
        }

    def _read_record_default(self, line: str, label_length: int) -> tuple[str, str, dict]:
        """Read a record in default format."""
        if "," in line:
            return self._read_record_tough4_free(line)
            
        data = self.readers[label_length](line)

        return data[0], data[1], {
            "nseq": data[2],
            "nadd": data[3:5],
            "permeability_direction": data[5],
            "nodal_distances": data[6:8],
            "interface_area": data[8],
            "gravity_cosine_angle": data[9],
            "radiant_emittance_factor": data[10],
        }

    def _write(self, parameters: dict, simulator: str, *args, **kwargs) -> list[str]:
        """Write CONNE block data."""
        # Return empty connection (i.e., single element)
        if not parameters.get("connections", {}):
            return []

        # Label length
        label_length = len(max(parameters["connections"], key=len)) // 2

        # Write records
        out = []

        if simulator == "tough4":
            if self.free_format:
                key = "5/tough4-free"
                get_values = self._get_values_tough4_free

            else:
                key = 5
                get_values = self._get_values_default

        else:
            key = label_length
            get_values = self._get_values_default

        for k, v in parameters["connections"].items():
            l1, l2 = k[:label_length], k[label_length:]
            out += self.writers[key]([l1, l2, *get_values(v)])

        return out

    def _get_values_tough4_free(self, data: dict) -> Sequence[Any]:
        """Get values for TOUGH4 free format."""
        return [
            data.get("permeability_direction"),
            *data.get("nodal_distances", [None, None]),
            data.get("interface_area"),
            data.get("gravity_cosine_angle"),
            data.get("radiant_emittance_factor"),
        ]

    def _get_values_default(self, data: dict) -> Sequence[Any]:
        """Get values for default format."""
        return [
            data.get("nseq"),
            *data.get("nadd", [None, None]),
            data.get("permeability_direction"),
            *data.get("nodal_distances", [None, None]),
            data.get("interface_area"),
            data.get("gravity_cosine_angle"),
            data.get("radiant_emittance_factor"),
        ]

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if CONNE block should be written."""
        return parameters.get("connections", {}) or parameters.get("elements", {})

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a CONNE block."""
        parameters.update(data["data"])
