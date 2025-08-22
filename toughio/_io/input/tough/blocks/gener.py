from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import Any, TextIO

import numpy as np

from .....core import DataBlock, FileIterator, RecordFormatter


class GENER(DataBlock):
    name = "GENER"
    formats = {
        0: ",".join(4 * ["14f"]),
        "0/tough4": ",".join(15 * ["14f"]),
        # Last integer is for KTAB value in TOUGHREACT
        5: "5s,5s,5d,5d,5d,5d,5s,4s,1s,10f,10f,10f,2d",
        6: "6s,5s,6d,4d,4d,5d,5s,4s,1s,10f,10f,10f,2d",
        7: "7s,5s,5d,4d,4d,5d,5s,4s,1s,10f,10f,10f,2d",
        8: "8s,5s,4d,4d,4d,5d,5s,4s,1s,10f,10f,10f,2d",
        9: "9s,5s,5d,3d,3d,5d,5s,4s,1s,10f,10f,10f,2d",
        "5/tough4-fixed": "5s,5s,5d,5d,5d,5d,5s,4s,1s,10f,10f,10f,10f,10f,10f",
        "5/tough4-free": "5s,5s,5d,5s,4s,1s,10f,10f,10f,10f,10f,10f",
    }
    multiples = {0}
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        simulator: str,
        *args,
        **kwargs,
    ) -> dict:
        """Read GENER block data."""

        def read_table(f: FileIterator, n: int, reader: RecordFormatter) -> list:
            table = []

            while len(table) < n:
                data = reader(f)
                table += self.prune_values(data)

            return table

        gener = {"generators": []}

        # Label length
        line = f.next()

        if not label_length:
            label_length = self.get_label_length(line[:9])

        label_format = f"{{:>{label_length}}}"

        # Read records
        flag = False

        if simulator == "tough4":
            if self.free_format:
                read_record = self._read_record_tough4_free

            else:
                read_record = self._read_record_tough4_fixed

            table_reader = self.readers["0/tough4"]

        else:
            read_record = partial(self._read_record_default, label_length=label_length)
            table_reader = self.readers[0]

        while True:
            if line.strip() and not line.startswith(("+++", ":::")):
                tmp, other = read_record(line)
                tmp["label"] = label_format.format(tmp["label"])
                ktab = other.get("ktab")  # TOUGHREACT
                ltab = other.get("ltab")

                if ltab and ltab > 1 and tmp["type"] != "DELV":
                    itab = other.get("itab")
                    keys = ["times", "rates"]
                    keys += (
                        ["specific_enthalpy"] if itab else []
                    )  # Specific enthalpy must be provided for time dependent injection

                    for key in keys:
                        tmp[key] = read_table(f, ltab, table_reader)

                else:
                    tmp.update(
                        {
                            "times": None,
                            "rates": other.get("rates"),
                            "specific_enthalpy": other.get("specific_enthalpy"),
                        }
                    )

                if ltab and tmp["type"] == "DELV":
                    tmp["n_layer"] = ltab

                if simulator == "toughreact" and ktab:
                    tmp["conductivity_times"] = read_table(f, ktab, table_reader)
                    tmp["conductivity_factors"] = read_table(f, ktab, table_reader)

                gener["generators"].append(self.prune_values(tmp))

            else:
                flag = line.startswith("+++")
                break

            try:
                line = f.next()

            except StopIteration:
                break

        return {
            "data": gener,
            "flag": flag,
            "label_length": label_length,
        }

    def _read_record_tough4_free(self, line: str) -> tuple[dict, dict]:
        """Read a record in free format for TOUGH4."""
        data = self.readers["5/tough4-free"](line)

        return {
            "label": data[0],
            "name": data[1],
            "type": data[4],
            "layer_thickness": data[8],
            "lots": self.prune_values(data[9:12]),
        }, {
            "ltab": data[2],
            "itab": data[5],
            "rates": data[6],
            "specific_enthalpy": data[7],
        }

    def _read_record_tough4_fixed(self, line: str) -> tuple[dict, dict]:
        """Read a record in fixed format for TOUGH4."""
        if "," in line:
            return self._read_record_tough4_free(line)

        data = self.readers["5/tough4-fixed"](line)

        return {
            "label": data[0],
            "name": data[1],
            "nseq": data[2],
            "nadd": data[3],
            "nads": data[4],
            "type": data[7],
            "layer_thickness": data[11],
            "lots": self.prune_values(data[12:15]),
        }, {
            "ltab": data[5],
            "itab": data[8],
            "rates": data[9],
            "specific_enthalpy": data[10],
        }

    def _read_record_default(self, line: str, label_length: int) -> tuple[dict, dict]:
        """Read a record in default format."""
        if "," in line:
            return self._read_record_tough4_free(line)

        data = self.readers[label_length](line)

        return {
            "label": data[0],
            "name": data[1],
            "nseq": data[2],
            "nadd": data[3],
            "nads": data[4],
            "type": data[7],
            "layer_thickness": data[11],
        }, {
            "ltab": data[5],
            "itab": data[8],
            "rates": data[9],
            "specific_enthalpy": data[10],
            "ktab": data[12],  # TOUGHREACT
        }

    def _write(
        self,
        parameters: dict,
        simulator: str = "tough",
        *args,
        **kwargs,
    ) -> list[str]:
        """Write GENER block data."""
        # Label length
        label_length = max(
            [len(generator.get("label", "")) for generator in parameters["generators"]]
        )
        label_length = max(label_length, 5)

        # Write records
        out = []

        if simulator == "tough4":
            if self.free_format:
                key = "5/tough4-free"
                get_values = self._get_values_tough4_free

            else:
                key = "5/tough4-fixed"
                get_values = self._get_values_tough4_fixed

        else:
            key = label_length
            get_values = self._get_values_default

        for v in parameters["generators"]:
            data = v.copy()

            # Table
            ltab = 1

            if data.get("times") is not None and isinstance(
                data.get("times"), (list, tuple, np.ndarray)
            ):
                ltab = len(data.get("times"))

                for k in ["rates", "specific_enthalpy"]:
                    if data.get(k) is not None:
                        if ltab == 1 and np.ndim(data.get(k)) == 1:
                            if len(data.get(k)) > 1:
                                raise ValueError()

                            data[k] = data.get(k)[0]

                        else:
                            if np.ndim(data.get(k)) != 1:
                                raise TypeError()

                            if ltab != len(data.get(k)):
                                raise ValueError()

            elif data.get("type") == "DELV" and data.get("n_layer") is not None:
                ltab = data.get("n_layer")

            else:
                for k in ["rates", "specific_enthalpy"]:
                    if np.ndim(data.get(k)) > 0:
                        if len(data.get(k)) > 1:
                            raise ValueError()

                        data[k] = data[k][0]

            itab = "1" if np.ndim(data.get("specific_enthalpy")) > 0 else None

            # TOUGHREACT
            ktab = len(data.get("conductivity_times", []))

            if (
                simulator == "toughreact"
                and len(data.get("conductivity_factors", [])) != ktab
            ):
                raise ValueError()

            # Record 1
            values = get_values(data, ltab, itab)

            if simulator == "toughreact":
                values.append(ktab)

            out += self.writers[key](values)

            if ltab > 1 and data.get("type") != "DELV":
                # Record 2
                out += self.writers[0](data.get("times"))

                # Record 3
                out += self.writers[0](data.get("rates"))

                # Record 4
                if data.get("specific_enthalpy") is not None:
                    if isinstance(
                        data.get("specific_enthalpy"), (list, tuple, np.ndarray)
                    ):
                        specific_enthalpy = data.get("specific_enthalpy")

                    else:
                        specific_enthalpy = np.full(ltab, data.get("specific_enthalpy"))

                    out += self.writers[0](specific_enthalpy)

            # TOUGHREACT
            if ktab:
                out += self.writers[0](data.get("conductivity_times"))
                out += self.writers[0](data.get("conductivity_factors"))

        return out

    def _get_values_tough4_free(
        self, data: dict, ltab: int, itab: int
    ) -> Sequence[Any]:
        """Get values for TOUGH4 free format."""
        return [
            data.get("label", ""),
            data.get("name"),
            ltab if ltab > 1 else None,
            None,
            data.get("type"),
            itab,
            None if ltab > 1 and data.get("type") != "DELV" else data.get("rates"),
            None
            if ltab > 1 and data.get("type") != "DELV"
            else data.get("specific_enthalpy"),
            data.get("layer_thickness"),
            *data.get("lots", []),
        ]

    def _get_values_tough4_fixed(
        self, data: dict, ltab: int, itab: int
    ) -> Sequence[Any]:
        """Get values for TOUGH4 fixed format."""
        return [
            data.get("label", ""),
            data.get("name"),
            data.get("nseq"),
            data.get("nadd"),
            data.get("nads"),
            ltab if ltab > 1 else None,
            None,
            data.get("type"),
            itab,
            None if ltab > 1 and data.get("type") != "DELV" else data.get("rates"),
            None
            if ltab > 1 and data.get("type") != "DELV"
            else data.get("specific_enthalpy"),
            data.get("layer_thickness"),
            *data.get("lots", []),
        ]

    def _get_values_default(self, data: dict, ltab: int, itab: int) -> Sequence[Any]:
        """Get values for default format."""
        return [
            data.get("label", ""),
            data.get("name"),
            data.get("nseq"),
            data.get("nadd"),
            data.get("nads"),
            ltab if ltab > 1 else None,
            None,
            data.get("type"),
            itab,
            None if ltab > 1 and data.get("type") != "DELV" else data.get("rates"),
            None
            if ltab > 1 and data.get("type") != "DELV"
            else data.get("specific_enthalpy"),
            data.get("layer_thickness"),
        ]

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if GENER block should be written."""
        return bool(parameters.get("generators", {}))

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a GENER block."""
        parameters.update(data["data"])
