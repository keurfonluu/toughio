from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, TextIO

import numpy as np

from .....core import DataBlock, FileIterator


class PARAM(DataBlock):
    name = "PARAM"
    formats = {
        1: f"2d,2d,4d,4d,4d,{','.join(24 * ["1d"])},10s,10f,10f",
        2: "10f,10f,10f,10f,5s,5s,10f,10f,10f",
        "2/tough4-free": "10f,10f,10f,10f,5s,10f,10f,10f",
        3: ",".join(8 * ["10f"]),
        4: "10f,10f,10s,10f,10f,10f",
        5: ",".join(4 * ["20f"]),
        6: "5d",
        7: "5s",
    }
    multiples = {3, 5}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        n_variables: int | Sequence[int],
        eos: str,
        *args,
        **kwargs
    ) -> dict:
        """Read PARAM block data."""
        param = {}

        # Record 1
        data = self.readers[1](f)
        param["options"] = {
            "n_iteration": data[0],
            "verbosity": data[1],
            "n_cycle": data[2],
            "n_second": data[3],
            "n_cycle_print": data[4],
            "temperature_dependence_gas": data[30],
            "effective_strength_vapor": data[31],
        }
        param["extra_options"] = {i + 1: x for i, x in enumerate(data[5:29]) if x is not None}

        # Record 2
        line = f.next()

        if self.free_format or "," in line:
            ishift = 0
            data = self.readers["2/tough4-free"](line)

        else:
            ishift = 1
            data = self.readers[2](line)

        param["options"].update(
            {
                "t_ini": data[0],
                "t_max": data[1],
                "t_steps": data[2],
                "t_step_max": data[3],
                "gravity": data[5 + ishift],
                "t_reduce_factor": data[6 + ishift],
                "mesh_scale_factor": data[7 + ishift],
            }
        )
        wdata = data[4]
        t_steps = data[2]

        if t_steps:
            if t_steps >= 0.0:
                param["options"]["t_steps"] = t_steps

            else:
                t_steps = int(-t_steps)
                param["options"]["t_steps"] = []

                for _ in range(t_steps):
                    data = self.readers[3](f)
                    param["options"]["t_steps"] += self.prune_values(data)

                if len(param["options"]["t_steps"]) == 1:
                    param["options"]["t_steps"] = param["options"]["t_steps"][0]

        # TOUGHREACT
        if wdata == "wdata":
            line = f.next()
            n = int(line.strip().split()[0])

            if n:
                param["options"]["react_wdata"] = []

                for _ in range(n):
                    data = self.readers[7](f)
                    param["options"]["react_wdata"].append(data[0].strip())

        # Record 3
        data = self.readers[4](f)
        param["options"].update(
            {
                "eps1": data[0],
                "eps2": data[1],
                "w_upstream": data[3],
                "w_newton": data[4],
                "derivative_factor": data[5],
            }
        )

        # Record 4 (ECO2M, TMVOC)
        if eos in {"eco2m", "tmvoc"}:
            data = self.readers[6](f)
            param["default"] = {"phase_composition": data[0]}

        # Record 5
        data = self.read_primary_variables(f, self.readers[5], n_variables)

        if "default" not in param:
            param["default"] = {}

        if any(x is not None for x in data):
            data = self.prune_values(data)
            param["default"]["initial_condition"] = data

        if not n_variables:
            n_variables = len(data)

        # Remove Nones
        param["options"] = self.prune_values(param["options"])
        param["extra_options"] = self.prune_values(param["extra_options"])

        return {
            "data": param,
            "n_variables": n_variables,
        }
        
    def _write(
        self,
        parameters: dict,
        eos: Optional[str] = None,
        simulator: str = "tough",
    ) -> list[str]:
        """Write PARAM block data."""
        out = []
        data = parameters.get("options", {})

        # Table
        t_steps = data.get("t_steps")

        if not isinstance(t_steps, (list, tuple, np.ndarray)):
            t_steps = [t_steps]

        # Record 1
        mop = [parameters.get("extra_options", {}).get(k + 1) for k in range(24)]
        values = [
            data.get("n_iteration"),
            data.get("verbosity"),
            data.get("n_cycle"),
            data.get("n_second"),
            data.get("n_cycle_print"),
            *mop,
            None,
            data.get("temperature_dependence_gas"),
            data.get("effective_strength_vapor"),
        ]
        out += self.writers[1](values)

        # Time steps
        ndlt = len(t_steps)

        if ndlt < 2:
            delten = t_steps[0] if ndlt else None

        else:
            delten = -((ndlt - 1) // 8 + 1)

        # Record 2
        react_wdata = data.get("react_wdata", [])
        values = [
            data.get("t_ini"),
            data.get("t_max"),
            delten,
            data.get("t_step_max"),
            "wdata" if react_wdata and simulator == "toughreact" else None,
        ]
        if not self.free_format:
            values.append(None)
        values += [
            data.get("gravity"),
            data.get("t_reduce_factor"),
            data.get("mesh_scale_factor"),
        ]
        out += (
            self.writers["2/tough4-free"](values)
            if self.free_format
            else self.writers[2](values)
        )

        # Record 2.1
        if ndlt > 1:
            values = [x for x in t_steps]
            out += self.writers[3](values)

        # TOUGHREACT
        if react_wdata and simulator == "toughreact":
            n = len(react_wdata)
            out += [f"{n}\n"]
            out += [f"{x}\n" for x in react_wdata]

        # Record 3
        values = [
            data.get("eps1"),
            data.get("eps2"),
            None,
            data.get("w_upstream"),
            data.get("w_newton"),
            data.get("derivative_factor"),
        ]
        out += self.writers[4](values)

        # Record 4 (ECO2M, TMVOC)
        if eos in {"eco2m", "tmvoc"}:
            out += self.writers[6]([parameters.get("default", {}).get("phase_composition")])

        # Record 5
        out += self.writers[5](parameters.get("default", {}).get("initial_condition", [None for _ in range(6)]))

        return out

    def _write_header(self) -> str:
        """Write the header for the PARAM block."""
        header = super()._write_header()

        if not self.free_format:
            header = header[:11] + "MOP: 123456789*123456789*1234" + header[40:]

        return header

    def _write_conditions(self, parameters: dict, eos: str, *args, **kwargs) -> bool:
        """Check if PARAM block should be written."""
        return (
            bool(parameters.get("options", {}))
            or bool(parameters.get("extra_options", {}))
            or any(parameters.get("default", {}).get("initial_condition", []))
            or (eos in {"eco2m", "tmvoc"} and parameters.get("default", {}).get("phase_composition") is not None)
        )

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a PARAM block."""
        parameters["options"] = data["data"]["options"]
        parameters["extra_options"] = data["data"]["extra_options"]
        parameters.setdefault("default", {}).update(data["data"]["default"])
