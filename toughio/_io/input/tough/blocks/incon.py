from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class INCON(DataBlock):
    name = "INCON"
    formats = {
        0: ",".join(4 * ["20f"]),
        5: "5s,5d,5d,15f,10f,10f,10f,10f,10f,10f",
        6: "6s,5d,4d,15f,10f,10f,10f,10f,10f,10f",
        7: "7s,4d,4d,15f,10f,10f,10f,10f,10f,10f",
        8: "8s,4d,3d,15f,10f,10f,10f,10f,10f,10f",
        9: "9s,3d,3d,15f,10f,10f,10f,10f,10f,10f",
        "5/eco2m": "5s,5d,5d,15f,2d",
        "6/eco2m": "6s,5d,4d,15f,2d",
        "7/eco2m": "7s,4d,4d,15f,2d",
        "8/eco2m": "8s,4d,3d,15f,2d",
        "9/eco2m": "9s,3d,3d,15f,2d",
        "5/tmvoc": "5s,5d,5d,15f,2d",
        "6/tmvoc": "6s,5d,4d,15f,2d",
        "7/tmvoc": "7s,4d,4d,15f,2d",
        "8/tmvoc": "8s,4d,3d,15f,2d",
        "9/tmvoc": "9s,3d,3d,15f,2d",
        "5/toughreact": "5s,5d,5d,15f,15f,15f,15f",
        "6/toughreact": "6s,5d,4d,15f,15f,15f,15f",
        "7/toughreact": "7s,4d,4d,15f,15f,15f,15f",
        "8/toughreact": "8s,4d,3d,15f,15f,15f,15f",
        "9/toughreact": "9s,3d,3d,15f,15f,15f,15f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        n_variables: int | Sequence[int],
        eos: str = None,
        simulator: str = "tough",
        *args,
        **kwargs
    ) -> dict:
        """Read INCON block data."""
        incon = {"initial_conditions": {}}

        # Label length
        line = f.next()

        if not label_length:
            label_length = self.get_label_length(line[:9])

        label_format = f"{{:>{label_length}}}"

        # Read records
        key = (
            f"{label_length}/{simulator}" if simulator == "toughreact"
            else f"{label_length}/{eos}" if eos in {"eco2m", "tmvoc"}
            else label_length
        )
        flag = False

        while True:
            if line.strip() and not line.startswith("+++"):
                # Record 1
                data = self.readers[key](line)
                label = label_format.format(data[0])
                incon["initial_conditions"][label] = {"porosity": data[3]}

                if simulator == "toughreact":
                    permeability = data[4] if len(set(data[4:7])) == 1 else data[4:7]
                    incon["initial_conditions"][label]["permeability"] = (
                        permeability if permeability else None
                    )

                elif eos in {"eco2m", "tmvoc"}:
                    incon["initial_conditions"][label]["phase_composition"] = data[4]

                else:
                    userx = self.prune_values(data[4:])
                    incon["initial_conditions"][label]["userx"] = userx if userx else None

                # Record 2
                data = self.read_primary_variables(f, self.readers[0], n_variables)
                data = self.prune_values(data)
                incon["initial_conditions"][label]["values"] = data

                if not n_variables:
                    n_variables = len(data)

            else:
                flag = line.startswith("+++")
                break

            line = f.next()

        incon["initial_conditions"] = {
            k: self.prune_values(v) for k, v in incon["initial_conditions"].items()
        }

        return {
            "data": incon,
            "flag": flag,
            "label_length": label_length,
            "n_variables": n_variables,
        }

    def _write(
        self,
        parameters: dict,
        eos: Optional[str] = None,
        simulator: str = "tough",
        *args,
        **kwargs,
    ) -> list[str]:
        """Write INCON block data."""
        # Label length
        label_length = len(max(parameters["initial_conditions"], key=len))
        label_length = max(label_length, 5)
        key = (
            f"{label_length}/{simulator}" if simulator == "toughreact"
            else f"{label_length}/{eos}" if eos in {"eco2m", "tmvoc"}
            else label_length
        )

        # Write records
        out = []

        for k, v in parameters["initial_conditions"].items():
            # Record 1
            values = [
                k,
                None,
                None,
                v.get("porosity"),
            ]

            if simulator == "toughreact":
                per = v.get("permeability")
                per = [per] * 3 if not np.ndim(per) else per

                if not (isinstance(per, (list, tuple, np.ndarray)) and len(per) == 3):
                    raise TypeError()

                values += [k for k in per]

            elif eos in {"eco2m", "tmvoc"}:
                values += [v.get("phase_composition")]

            else:
                values += list(v.get("userx", [None] * 6))

            out += self.writers[key](values)

            # Record 2
            out += self.writers[0](v.get("values", [None] * 4))

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if INCON block should be written."""
        return bool(parameters.get("initial_conditions", {}))

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a INCON block."""
        parameters.update(data["data"])