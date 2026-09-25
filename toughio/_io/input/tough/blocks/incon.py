from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import Any, Optional, TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class INCON(DataBlock):
    name = "INCON"
    formats = {
        0: ",".join(12 * ["20f"]),
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
        "5/tough4-fixed": "5s,5d,5d,15f,5S,10f,10f,10f",
        "5/tough4-free": "5s,15f,5S,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        n_variables: int | Sequence[int],
        eos: str,
        simulator: str,
        *args,
        **kwargs,
    ) -> dict:
        """Read INCON block data."""
        incon = {"initial_conditions": {}}

        # Label length
        line = f.next()

        if not label_length:
            label_length = self.get_label_length(line[:9])

        label_format = f"{{:>{label_length}}}"

        # Read records
        flag = False

        if simulator == "toughreact":
            read_record = partial(
                self._read_record_toughreact, label_length=label_length
            )

        elif simulator == "tough4":
            if self.free_format:
                read_record = self._read_record_tough4_free

            else:
                read_record = self._read_record_tough4_fixed

        elif eos in {"eco2m", "tmvoc"}:
            read_record = partial(
                self._read_record_eco2m_tmvoc, label_length=label_length
            )

        else:
            read_record = partial(self._read_record_default, label_length=label_length)

        while True:
            if line.strip() and not line.startswith(("+++", ":::")):
                # Record 1
                label, tmp = read_record(line)
                label = label_format.format(label)
                incon["initial_conditions"][label] = self.prune_values(tmp)

                # Record 2
                data = self.read_primary_variables(f, self.readers[0], n_variables)
                data = self.prune_values(data)
                incon["initial_conditions"][label]["values"] = data

                if not n_variables:
                    n_variables = len(data)

            else:
                flag = line.startswith(("+++", ":::"))
                break

            try:
                line = f.next()

            except StopIteration:
                break

        return {
            "data": incon,
            "flag": flag,
            "label_length": label_length,
            "n_variables": n_variables,
        }

    def _read_record_toughreact(self, line: str, label_length: int) -> tuple[str, dict]:
        """Read record 1 for TOUGHREACT."""
        data = self.readers[f"{label_length}/toughreact"](line)
        permeability = data[4:7]
        permeability = permeability[0] if len(set(permeability)) == 1 else permeability

        return data[0], {
            "porosity": data[3],
            "permeability": permeability if permeability else None,
        }

    def _read_record_tough4_free(self, line: str) -> tuple[str, dict]:
        """Read record 1 for TOUGH4 in free format."""
        data = self.readers[f"5/tough4-free"](line)
        permeability = data[3:6]
        permeability = permeability[0] if len(set(permeability)) == 1 else permeability

        return data[0], {
            "porosity": data[1],
            "phase_state": data[2],
            "permeability": permeability if permeability else None,
        }

    def _read_record_tough4_fixed(self, line: str) -> tuple[str, dict]:
        """Read record 1 for TOUGH4 in fixed format."""
        if "," in line:
            return self._read_record_tough4_free(line)

        data = self.readers[f"5/tough4-fixed"](line)
        permeability = data[5:8]
        permeability = permeability[0] if len(set(permeability)) == 1 else permeability

        return data[0], {
            "porosity": data[3],
            "phase_state": data[4],
            "permeability": permeability if permeability else None,
        }

    def _read_record_eco2m_tmvoc(
        self, line: str, label_length: int
    ) -> tuple[str, dict]:
        """Read record 1 for ECO2M and TMVOC."""
        data = self.readers[f"{label_length}/eco2m"](line)

        return data[0], {
            "porosity": data[3],
            "phase_composition": data[4],
        }

    def _read_record_default(self, line: str, label_length: int) -> tuple[str, dict]:
        """Read record 1 for default format."""
        if "," in line:
            return self._read_record_tough4_free(line)

        data = self.readers[label_length](line)
        userx = self.prune_values(data[4:])

        return data[0], {
            "porosity": data[3],
            "userx": userx if userx else None,
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

        # Write records
        out = []

        if simulator == "toughreact":
            key = f"{label_length}/toughreact"
            get_values = self._get_values_toughreact

        elif simulator == "tough4":
            if self.free_format:
                key = f"5/tough4-free"
                get_values = self._get_values_tough4_free

            else:
                key = f"5/tough4-fixed"
                get_values = self._get_values_tough4_fixed

        elif eos in {"eco2m", "tmvoc"}:
            key = f"{label_length}/{eos}"
            get_values = self._get_values_eco2m_tmvoc

        else:
            get_values = self._get_values_default
            key = label_length

        n_variables = None

        for k, v in parameters["initial_conditions"].items():
            # Record 1
            out += self.writers[key]([k, *get_values(v)])

            # Record 2
            values = v.get("values")

            if values is None:
                continue

            if simulator == "tough4" and self.free_format:
                out += self.writers[0](values)

            else:
                if n_variables is None:
                    n_variables = len(values)

                out += self.write_primary_variables(
                    values, self.writers[0], n_variables
                )

        return out

    @staticmethod
    def _get_values_toughreact(data: dict) -> Sequence[Any]:
        """Get values of record 1 for TOUGHREACT."""
        per = data.get("permeability")
        per = [per] * 3 if np.ndim(per) == 0 else per

        return [
            None,
            None,
            data.get("porosity"),
            *per,
        ]

    @staticmethod
    def _get_values_tough4_free(data: dict) -> Sequence[Any]:
        """Get values of record 1 for TOUGH4 in free format."""
        per = data.get("permeability")
        per = [per] * 3 if np.ndim(per) == 0 else per

        return [
            data.get("porosity"),
            data.get("phase_state"),
            *per,
        ]

    @staticmethod
    def _get_values_tough4_fixed(data: dict) -> Sequence[Any]:
        """Get values of record 1 for TOUGH4 in fixed format."""
        per = data.get("permeability")
        per = [per] * 3 if np.ndim(per) == 0 else per

        return [
            None,
            None,
            data.get("porosity"),
            data.get("phase_state"),
            *per,
        ]

    @staticmethod
    def _get_values_eco2m_tmvoc(data: dict) -> Sequence[Any]:
        """Get values of record 1 for ECO2M and TMVOC."""
        return [
            None,
            None,
            data.get("porosity"),
            data.get("phase_composition"),
        ]

    @staticmethod
    def _get_values_default(data: dict) -> Sequence[Any]:
        """Get values of record 1 for default format."""
        userx = data.get("userx", [None] * 6)

        return [
            None,
            None,
            data.get("porosity"),
            *userx,
        ]

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
