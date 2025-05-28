from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class CONNE(DataBlock):
    name = "CONNE"
    formats = {
        5: "10s,5d,5d,5d,5d,10f,10f,10f,10f,10f",
        6: "12s,5d,4d,4d,5d,10f,10f,10f,10f,10f",
        7: "14s,5d,3d,3d,5d,10f,10f,10f,10f,10f",
        8: "16s,3d,3d,3d,5d,10f,10f,10f,10f,10f",
        9: "18s,3d,2d,2d,5d,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
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

        while True:
            if line.strip() and not line.startswith("+++"):
                data = self.readers[label_length](line)
                label = label_format.format(data[0])
                conne["connections"][label] = {
                    "nseq": data[1],
                    "nadd": data[2:4],
                    "permeability_direction": data[4],
                    "nodal_distances": data[5:7],
                    "interface_area": data[7],
                    "gravity_cosine_angle": data[8],
                    "radiant_emittance_factor": data[9],
                }

            else:
                flag = line.startswith("+++")
                break

            line = f.next()

        conne["connections"] = {k: self.prune_values(v) for k, v in conne["connections"].items()}

        return {
            "data": conne,
            "flag": flag,
            "label_length": label_length,
        }

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write CONNE block data."""
        # Return empty connection (i.e., single element)
        if not parameters.get("connections", {}):
            return []

        # Label length
        label_length = len(max(parameters["connections"], key=len)) // 2

        # Write records
        out = []

        for k, v in parameters["connections"].items():
            nadd = v.get("nadd", [None, None])
            nodal_distances = v.get("nodal_distances", [None, None])
            values = [
                k,
                v.get("nseq"),
                nadd[0],
                nadd[1],
                v.get("permeability_direction"),
                nodal_distances[0],
                nodal_distances[1],
                v.get("interface_area"),
                v.get("gravity_cosine_angle"),
                v.get("radiant_emittance_factor"),
            ]
            out += self.writers[label_length](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if CONNE block should be written."""
        return parameters.get("connections", {}) or parameters.get("elements", {})
