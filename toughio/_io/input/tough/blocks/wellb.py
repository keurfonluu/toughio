from __future__ import annotations

from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class WELLB(DataBlock):
    name = "WELLB"
    formats = {
        1: "10f,10f,10f,10f,10f,10f,10s",
        "2/GEOTH": "5s,5f,10f,10f,10f,10f,10f,10f,10f,10f,10f",
        "2/REGFX": "10s,20s,10f,10f,10f,10f,10d",
        "2/OFFMA": "10s," + ",".join(["20s"] * 10),
        "2/FREEE": "10s," + ",".join(["10s"] * 10),
        "2/ROCKS": "5s,10f,10f,10f,10f,10f,10f,10f",
        3: "10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        parameters: dict,
        *args,
        **kwargs
    ) -> dict:
        """Read WELLB block data."""
        from . import registered_blocks

        wellb = {}

        # Record 1
        data = self.readers[1](f)
        wellb["solid_fraction"] = data[0]
        wellb["cmax"] = data[1]
        wellb["ku_crit"] = data[2]
        wellb["well_fraction"] = data[3]
        wellb["roughness"] = data[4]
        wellb["sg1"] = data[5]

        if data[6]:
            wellb["heat_exchange"] = data[6].lower() == "true"

        # Record 2
        rocks = tuple(parameters.get("rocks", {}))
        registered_blocks = tuple([block.name for block in registered_blocks])

        while True:
            i = f.tell()
            line = f.next(skip_empty=True, comments=("//", "!"))

            if line.startswith(registered_blocks):
                f.seek(i, increment=-1)
                break

            if line.startswith("GEOTH"):
                data = self.readers["2/GEOTH"](line)
                tmp = {
                    "well_only": int(data[1]) == 0,
                    "temperature_ref": data[2],
                    "temperature_grad": self.prune_values(data[3::2]),
                    "temperature_z": self.prune_values(data[4::2]),
                }
                tmp["temperature_grad"] = tmp["temperature_grad"][0] if len(tmp["temperature_grad"]) == 1 else tmp["temperature_grad"]
                tmp["temperature_z"] = tmp["temperature_z"][0] if len(tmp["temperature_z"]) == 1 else tmp["temperature_z"]
                wellb["geothermal"] = self.prune_values(tmp)

            elif line.startswith("REGFX"):
                data = self.readers["2/REGFX"](line)
                tmp = {
                    "label": data[1],
                    "rate_ini": data[2],
                    "time_max": data[3],
                    "rate_max": data[4],
                    "rate_end": data[5],
                }
                n_steps = data[6]

                if n_steps:
                    for _ in range(n_steps):
                        data = self.readers[3](f)
                        tmp.setdefault("times", []).append(data[0])
                        tmp.setdefault("rates", []).append(data[1])

                wellb.setdefault("flows", []).append(self.prune_values(tmp))

            elif line.startswith("OFFMA"):
                data = self.readers["2/OFFMA"](line)
                wellb["branches"] = self.prune_values(data[1:])

            elif line.startswith("FREEE"):
                data = self.readers["2/FREEE"](line)
                wellb["free_elements"] = self.prune_values(data[1:])

            elif line.startswith(rocks):
                data = self.readers["2/ROCKS"](line)
                tmp = {
                    "roughness": data[1],
                    "screen_fraction": data[2],
                    "area": data[3],
                    "factor": data[4],
                    "diameter": data[5],
                    "perimeter": data[6],
                    "heat_exchange": data[7],
                }
                parameters["rocks"][data[0]].update(self.prune_values(tmp))

            else:
                raise ValueError(f"invalid action word '{data[0]}'")

        return {"wellbore": self.prune_values(wellb)}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write WELLB block data."""
        out = []
        data = parameters.get("wellbore", {})

        # Record 1
        values = [
            data.get("solid_fraction"),
            data.get("cmax"),
            data.get("ku_crit"),
            data.get("well_fraction"),
            data.get("roughness"),
            data.get("sg1"),
        ]
        
        if "heat_exchange" in data:
            values.append("true" if data.get("heat_exchange") else "false")

        out += self.writers[1](values)

        # Record 2
        # Geothermal
        if "geothermal" in data:
            well_only = int(not data.get("geothermal").get("well_only", True))
            values = [
                "GEOTH",
                well_only,
                data.get("geothermal").get("temperature_ref"),
            ]

            grads = data.get("geothermal").get("temperature_grad", [])
            elevs = data.get("geothermal").get("temperature_z", [])
            
            grads = [grads] if np.ndim(grads) == 0 else grads
            elevs = [elevs] if np.ndim(elevs) == 0 else elevs

            for grad, z in zip(grads, elevs):
                values += [grad, z]

            out += self.writers["2/GEOTH"](values)

        # Flows
        for flow in data.get("flows", []):
            values = [
                "REGFX",
                flow.get("label", ""),
                flow.get("rate_ini"),
                flow.get("time_max"),
                flow.get("rate_max"),
                flow.get("rate_end"),
                len(flow.get("times", [])),
            ]
            out += self.writers["2/REGFX"](values)

            for time, rate in zip(flow.get("times", []), flow.get("rates", [])):
                out += self.writers[3]([time, rate])

        # Branches
        if "branches" in data:
            values = ["OFFMA", *data.get("branches", [])]
            out += self.writers["2/OFFMA"](values)

        # Free elements
        if "free_elements" in data:
            values = ["FREEE", *data.get("free_elements", [])]
            out += self.writers["2/FREEE"](values)

        # Rocks
        wellbore_keys = {
            "roughness",
            "screen_fraction",
            "area",
            "factor",
            "diameter",
            "perimeter",
            "heat_exchange",
        }

        for k, v in parameters.get("rocks", {}).items():
            data = {
                k: v
                for k, v in parameters.get("default", {}).items()
                if k in wellbore_keys
            }
            data.update(v)

            if not wellbore_keys.intersection(data):
                continue

            values = [
                k,
                data.get("roughness"),
                data.get("screen_fraction"),
                data.get("area"),
                data.get("factor"),
                data.get("diameter"),
                data.get("perimeter"),
                data.get("heat_exchange"),
            ]
            out += self.writers["2/ROCKS"](values)

        return out

    def _write_conditions(self, parameters: dict, simulator: str, *args, **kwargs) -> bool:
        """Check if WELLB block should be written."""
        return bool(parameters.get("wellbore", {})) and simulator == "tough4"
