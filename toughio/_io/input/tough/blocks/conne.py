from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import Any, TextIO

from .....core import DataBlock, FileIterator


class CONNE(DataBlock):
    name = "CONNE"
    formats = {
        5: "10s,5d,5d,5d,5d,10f,10f,10f,10f,10f",
        6: "12s,5d,4d,4d,5d,10f,10f,10f,10f,10f",
        7: "14s,5d,3d,3d,5d,10f,10f,10f,10f,10f",
        8: "16s,3d,3d,3d,5d,10f,10f,10f,10f,10f",
        9: "18s,3d,2d,2d,5d,10f,10f,10f,10f,10f",
        "5/tough4-free": "10s,5d,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True
    _with_nseq = True

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
            if self.free_format and not self._with_nseq:
                read_record = self._read_record_tough4_free

            else:
                read_record = partial(self._read_record_default, label_length=5)

        else:
            read_record = partial(self._read_record_default, label_length=label_length)

        while True:
            if line.strip() and not line.startswith("+++"):
                label, tmp = read_record(line)
                label = label_format.format(label)
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

    def _read_record_tough4_free(self, line: str) -> tuple[str, dict]:
        """Read a record in free format for TOUGH4."""
        data = self.readers["5/tough4-free"](line)

        return data[0], {
            "permeability_direction": data[1],
            "nodal_distances": data[2:4],
            "interface_area": data[4],
            "gravity_cosine_angle": data[5],
            "radiant_emittance_factor": data[6],
        }

    def _read_record_default(self, line: str, label_length: int) -> tuple[str, dict]:
        """Read a record in default format."""
        data = self.readers[label_length](line)

        return data[0], {
            "nseq": data[1],
            "nadd": data[2:4],
            "permeability_direction": data[4],
            "nodal_distances": data[5:7],
            "interface_area": data[7],
            "gravity_cosine_angle": data[8],
            "radiant_emittance_factor": data[9],
        }

    def _write(self, parameters: dict, simulator: str, *args, **kwargs) -> list[str]:
        """Write CONNE block data."""
        # Return empty connection (i.e., single element)
        if not parameters.get("connections", {}):
            return []

        # Label length
        label_length = len(max(parameters["connections"], key=len)) // 2

        # Write records
        if simulator == "tough4":
            if self.free_format and not self._with_nseq:
                key = "5/tough4-free"
                get_values = self._get_values_tough4_free

            else:
                key = 5
                get_values = self._get_values_default

        else:
            key = label_length
            get_values = self._get_values_default

        out = [
            self.writers[key]([k, *get_values(v)])[0]
            for k, v in parameters["connections"].items()
        ]

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
