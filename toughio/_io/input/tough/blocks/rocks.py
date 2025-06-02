from __future__ import annotations

from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class ROCKS(DataBlock):
    name = "ROCKS"
    formats = {
        1: "5s,5d,10f,10f,10f,10f,10f,10f,10f",
        2: "10f,10f,10f,10f,10f,10f,10f,10f,10f",  # Tortuosity can be <0 in TOUGHREACT
        # TOUGHREACT
        3: "5d,5s,10f,10f,10f",
        4: "5d,5s,14f,14f,14f,14f",
        5: "5d,5s,10f,10f,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        simulator: str,
        *args,
        **kwargs
    ) -> dict:
        """Read ROCKS block data."""
        rocks = {"rocks": {}}

        while True:
            line = f.next()

            if line.strip():
                # Record 1
                data = self.readers[1](line)
                rock = data[0]
                rocks["rocks"][rock] = {
                    "density": data[2],
                    "porosity": data[3],
                    "permeability": data[4] if len(set(data[4:7])) == 1 else data[4:7],
                    "conductivity": data[7],
                    "specific_heat": data[8],
                }

                nad = data[1] if data[1] else 0

                if nad:
                    # Record 2
                    data = self.readers[2](f)
                    rocks["rocks"][rock].update(
                        {
                            "compressibility": data[0],
                            "expansivity": data[1],
                            "conductivity_dry": data[2],
                            "tortuosity": data[3],
                            "klinkenberg_parameter": data[4],
                            "distribution_coefficient_3": data[5],
                            "distribution_coefficient_4": data[6],
                            "tortuosity_exponent": data[7],
                            "porosity_crit": data[8],
                        }
                    )

                if nad >= 2:
                    # TOUGHREACT
                    if simulator == "toughreact" and nad >= 4:
                        line = f.next()
                        if line.strip():
                            rocks["rocks"][rock]["react_tp"] = self.read_model_record(
                                line, self.readers[3]
                            )

                        line = f.next()
                        if line.strip():
                            rocks["rocks"][rock]["react_hcplaw"] = self.read_model_record(
                                line, self.readers[4],
                            )

                    # Relative permeability / Capillary pressure
                    for key in ["relative_permeability", "capillarity"]:
                        rocks["rocks"][rock][key] = self.read_model_record(
                            f, self.readers[5],
                        )

            else:
                break

        rocks["rocks"] = {k: self.prune_values(v) for k, v in rocks["rocks"].items()}

        return rocks

    def _write(self, parameters: dict, simulator: str, *args, **kwargs) -> list[str]:
        """Write ROCKS block data."""
        out = []

        for k, v in parameters["rocks"].items():
            data = {
                k: v
                for k, v in parameters.get("default", {}).items()
                if k not in {
                    "initial_condition",
                    "relative_permeability",
                    "capillarity",
                    "phase_composition",
                    "react_tp",
                    "react_hcplaw",
                }
            }
            data.update(v)

            # Number of additional lines to write per rock
            cond = any(
                data.get(k) is not None
                for k in [
                    "compressibility",
                    "expansivity",
                    "conductivity_dry",
                    "tortuosity",
                    "klinkenberg_parameter",
                    "distribution_coefficient_3",
                    "distribution_coefficient_4",
                    "tortuosity_exponent",
                    "porosity_crit",
                ]
            )
            nad = 2 if "relative_permeability" in data or "capillarity" in data else int(cond)

            if simulator == "toughreact":
                nad = 4 if "react_tp" in data else nad
                nad = 5 if "react_hcplaw" in data else nad

            # Permeability
            per = data.get("permeability", None)
            per = [per] * 3 if not np.ndim(per) else per
            
            if not (isinstance(per, (list, tuple, np.ndarray)) and len(per) == 3):
                raise TypeError()

            # Record 1
            values = [
                k,
                nad if nad else "",
                data.get("density"),
                data.get("porosity"),
                per[0],
                per[1],
                per[2],
                data.get("conductivity"),
                data.get("specific_heat"),
            ]
            out += self.writers[1](values)

            # Record 2
            if cond:
                values = [
                    data.get(key) for key in [
                        "compressibility",
                        "expansivity",
                        "conductivity_dry",
                        "tortuosity",
                        "klinkenberg_parameter",
                        "distribution_coefficient_3",
                        "distribution_coefficient_4",
                        "tortuosity_exponent",
                        "porosity_crit",
                    ]
                ]
                out += self.writers[2](values)

            else:
                out += self.writers[2]() if nad >= 2 else []

            # TOUGHREACT
            if nad >= 4:
                out += self.write_model_record(data, "react_tp", self.writers[3])
                out += self.write_model_record(data, "react_hcplaw", self.writers[4])

            # Relative permeability / Capillary pressure
            if nad >= 2:
                out += self.write_model_record(data, "relative_permeability", self.writers[5])
                out += self.write_model_record(data, "capillarity", self.writers[5])

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if ROCKS block should be written."""
        return bool(parameters.get("rocks", {}))
