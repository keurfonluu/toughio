from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class ELEME(DataBlock):
    name = "ELEME"
    formats = {
        5: "5s,5d,5d,5s,10f,10f,10f,10f,10f,10f",
        6: "6s,5d,4d,5s,10f,10f,10f,10f,10f,10f",
        7: "7s,4d,4d,5s,10f,10f,10f,10f,10f,10f",
        8: "8s,4d,3d,5s,10f,10f,10f,10f,10f,10f",
        9: "9s,3d,3d,5s,10f,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
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
        while True:
            if line.strip():
                data = self.readers[label_length](line)
                label = label_format.format(data[0])
                label = label.lstrip() if label.lstrip().isalpha() else label
                rock = data[3]

                if rock:
                    rock = rock.strip()
                    rock = int(rock) if rock.isdigit() else rock

                eleme["elements"][label] = {
                    "nseq": data[1],
                    "nadd": data[2],
                    "material": rock,
                    "volume": data[4],
                    "heat_exchange_area": data[5],
                    "permeability_modifier": data[6],
                    "center": data[7:10],
                }

            else:
                break

            line = f.next()

        eleme["elements"] = {k: self.prune_values(v) for k, v in eleme["elements"].items()}

        return {
            "data": eleme,
            "label_length": label_length,
        }

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write ELEME block data."""
        # Label length
        label_length = len(max(parameters["elements"], key=len))
        
        # Write records
        out = []

        for k, v in parameters["elements"].items():
            material = v.get("material", "")
            material = f"{material:>5}" if isinstance(material, int) else material
            center = v.get("center", [None, None, None])

            values = [
                k,
                v.get("nseq"),
                v.get("nadd"),
                material,
                v.get("volume"),
                v.get("heat_exchange_area"),
                v.get("permeability_modifier"),
                *center
            ]
            out += self.writers[label_length](values)

        return out

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
