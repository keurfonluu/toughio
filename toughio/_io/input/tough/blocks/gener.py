from __future__ import annotations

from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator, RecordFormatter


class GENER(DataBlock):
    name = "GENER"
    formats = {
        0: ",".join(4 * ["14f"]),
        # Last integer is for KTAB value in TOUGHREACT
        5: "5s,5s,5d,5d,5d,5d,5s,4s,1s,10f,10f,10f,2d",
        6: "6s,5s,6d,4d,4d,5d,5s,4s,1s,10f,10f,10f,2d",
        7: "7s,5s,5d,4d,4d,5d,5s,4s,1s,10f,10f,10f,2d",
        8: "8s,5s,4d,4d,4d,5d,5s,4s,1s,10f,10f,10f,2d",
        9: "9s,5s,5d,3d,3d,5d,5s,4s,1s,10f,10f,10f,2d",
    }
    multiples = {0}
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        simulator: str = "tough",
        *args,
        **kwargs
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

        while True:
            if line.strip() and not line.startswith("+++"):
                data = self.readers[label_length](line)
                tmp = {
                    "label": label_format.format(data[0]),
                    "name": data[1],
                    "nseq": data[2],
                    "nadd": data[3],
                    "nads": data[4],
                    "type": data[7],
                    "layer_thickness": data[11],
                }
                ktab = data[12]  # TOUGHREACT
                ltab = data[5]

                if ltab and ltab > 1 and tmp["type"] != "DELV":
                    itab = data[8]
                    keys = ["times", "rates"]
                    keys += (
                        ["specific_enthalpy"] if itab else []
                    )  # Specific enthalpy must be provided for time dependent injection

                    for key in keys:
                        tmp[key] = read_table(f, ltab, self.readers[0])

                else:
                    tmp.update(
                        {
                            "times": None,
                            "rates": data[9],
                            "specific_enthalpy": data[10],
                        }
                    )

                if ltab and tmp["type"] == "DELV":
                    tmp["n_layer"] = ltab

                if simulator == "toughreact" and ktab:
                    tmp["conductivity_times"] = read_table(f, ktab, self.readers[0])
                    tmp["conductivity_factors"] = read_table(f, ktab, self.readers[0])

                gener["generators"].append(tmp)

            else:
                flag = line.startswith("+++")
                break

            line = f.next()

        return {
            "data": {
                "generators": [
                    self.prune_values(generator)
                    for generator in gener["generators"]
                ]
            },
            "flag": flag,
            "label_length": label_length,
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
            [
                len(generator.get("label", ""))
                for generator in parameters["generators"]
            ]
        )
        label_length = max(label_length, 5)

        # Write records
        out = []

        for v in parameters["generators"]:
            data = v.copy()

            # Table
            ltab = 1

            if data.get("times") is not None and isinstance(
                data.get("times"), (list, tuple, np.ndarray)
            ):
                ltab = len(data.get("times"))

                for key in ["rates", "specific_enthalpy"]:
                    if data.get(key) is not None:
                        if ltab == 1 and np.ndim(data.get(key)) == 1:
                            if len(data.get(key)) > 1:
                                raise ValueError()

                            data[key] = data.get(key)[0]

                        else:
                            if np.ndim(data.get(key)) != 1:
                                raise TypeError()

                            if ltab != len(data.get(key)):
                                raise ValueError()

            elif data.get("type") == "DELV" and data.get("n_layer") is not None:
                ltab = data.get("n_layer")

            else:
                for key in ["rates", "specific_enthalpy"]:
                    if np.ndim(data.get(key)) > 0:
                        if len(data.get(key)) > 1:
                            raise ValueError()

                        data[key] = data[key][0]

            itab = (
                "1"
                if isinstance(data.get("specific_enthalpy"), (list, tuple, np.ndarray))
                else None
            )

            # TOUGHREACT
            ktab = len(data.get("conductivity_times", []))

            if (
                simulator == "toughreact"
                and len(data.get("conductivity_factors", [])) != ktab
            ):
                raise ValueError()

            # Record 1
            values = [
                data.get("label", ""),
                data.get("name"),
                data.get("nseq"),
                data.get("nadd"),
                data.get("nads"),
                ltab if ltab > 1 else 1,
                None,
                data.get("type"),
                itab,
                None if ltab > 1 and data.get("type") != "DELV" else data.get("rates"),
                None if ltab > 1 and data.get("type") != "DELV" else data.get("specific_enthalpy"),
                data.get("layer_thickness"),
                ktab if ktab else None,
            ]
            out += self.writers[label_length](values)

            if ltab > 1 and data.get("type") != "DELV":
                # Record 2
                out += self.writers[0](data.get("times"))

                # Record 3
                out += self.writers[0](data.get("rates"))

                # Record 4
                if data.get("specific_enthalpy") is not None:
                    if isinstance(data.get("specific_enthalpy"), (list, tuple, np.ndarray)):
                        specific_enthalpy = data.get("specific_enthalpy")

                    else:
                        specific_enthalpy = np.full(ltab, data.get("specific_enthalpy"))

                    out += self.writers[0](specific_enthalpy)

            # TOUGHREACT
            if ktab:
                out += self.writers[0](data.get("conductivity_times"))
                out += self.writers[0](data.get("conductivity_factors"))

        return out

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
