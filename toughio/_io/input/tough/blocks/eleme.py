from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import Any, TextIO

from .....core import DataBlock, FileIterator


class ELEME(DataBlock):
    name = "ELEME"
    formats = {
        5: "5s,5d,5d,5s,10f,10f,10f,10f,10f,10f",
        6: "6s,5d,4d,5s,10f,10f,10f,10f,10f,10f",
        7: "7s,4d,4d,5s,10f,10f,10f,10f,10f,10f",
        8: "8s,4d,3d,5s,10f,10f,10f,10f,10f,10f",
        9: "9s,3d,3d,5s,10f,10f,10f,10f,10f,10f",
        "5/tough4-free": "5s,5s,10f,10f,10f,10f,10f,10f",
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
        """Read ELEME block data."""
        eleme = {"elements": {}}

        # Label length
        line = f.next()

        if not label_length:
            label_length = self.get_label_length(line[:9])

        label_format = f"{{:>{label_length}}}"

        # Read records
        if simulator == "tough4":
            if self.free_format:
                read_record = self._read_record_tough4_free

            else:
                read_record = partial(self._read_record_default, label_length=5)

        else:
            read_record = partial(self._read_record_default, label_length=label_length)

        while True:
            if line.strip():
                label, tmp = read_record(line)
                label = label_format.format(label)
                label = label.lstrip() if label.lstrip().isalpha() else label

                if tmp["material"]:
                    tmp["material"] = tmp["material"].strip()
                    tmp["material"] = int(tmp["material"]) if tmp["material"].isdigit() else tmp["material"]

                eleme["elements"][label] = self.prune_values(tmp)

            else:
                break

            try:
                line = f.next()

            except StopIteration:
                break

        return {
            "data": eleme,
            "label_length": label_length,
        }

    def _read_record_tough4_free(self, line: str) -> tuple[str, dict]:
        """Read a record in free format for TOUGH4."""
        data = self.readers["5/tough4-free"](line)

        return data[0], {
            "material": data[1],
            "volume": data[2],
            "heat_exchange_area": data[3],
            "permeability_modifier": data[4],
            "center": data[5:8],
        }

    def _read_record_default(self, line: str, label_length) -> tuple[str, dict]:
        """Read a record in default format."""
        if "," in line:
            return self._read_record_tough4_free(line)
            
        data = self.readers[label_length](line)

        return data[0], {
            "nseq": data[1],
            "nadd": data[2],
            "material": data[3],
            "volume": data[4],
            "heat_exchange_area": data[5],
            "permeability_modifier": data[6],
            "center": data[7:10],
        }

    def _write(self, parameters: dict, simulator: str, *args, **kwargs) -> list[str]:
        """Write ELEME block data."""
        # Label length
        label_length = len(max(parameters["elements"], key=len))
        
        # Write records
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

        out = [
            self.writers[key]([k, *get_values(v)])[0]
            for k, v in parameters["elements"].items()
        ]
        
        return out

    @staticmethod
    def _get_values_tough4_free(data: dict) -> Sequence[Any]:
        """Get values for TOUGH4 free format."""
        material = data.get("material", "")
        material = f"{material:>5}" if isinstance(material, int) else material

        return [
            material,
            data.get("volume"),
            data.get("heat_exchange_area"),
            data.get("permeability_modifier"),
            *data.get("center", [None, None, None])
        ]

    @staticmethod
    def _get_values_default(data: dict) -> Sequence[Any]:
        """Get values for default format."""
        material = data.get("material", "")
        material = f"{material:>5}" if isinstance(material, int) else material

        return [
            data.get("nseq"),
            data.get("nadd"),
            material,
            data.get("volume"),
            data.get("heat_exchange_area"),
            data.get("permeability_modifier"),
            *data.get("center", [None, None, None])
        ]

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if ELEME block should be written."""
        return bool(parameters.get("elements", {}))

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a ELEME block."""
        parameters.update(data["data"])
        parameters["coordinates"] = False
