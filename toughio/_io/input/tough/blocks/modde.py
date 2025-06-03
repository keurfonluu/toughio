from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class MODDE(DataBlock):
    name = "MODDE"
    formats = {
        1: "10s,10s,10s",
        2: "5d",
        3: "5s,5s,5s,5s,5s",
    }
    _components = {
        "eos1": "water2",
        "eos7": "brine",
        "eco2": "co2",
    }

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read MODDE block data."""
        modde = {}

        # Record 1
        data = self.readers[1](f)
        modde["eos"] = data[0].lower()
        modde["incon_type"] = data[1]
        modde["cubic_type"] = data[2]

        # Record 2
        data = self.readers[2](f)
        modde["label_length"] = data[0]

        # Record 3
        data = self.readers[3](f)

        if data[0]:
            modde["isothermal"] = data[0].lower() == "false"

        if data[1]:
            modde["do_diffusion"] = data[1].lower() == "true"

        if data[2] and modde["eos"] in self._components:
            modde[f"include_{self._components[modde['eos']]}"] = data[2].lower() == "true"

        if data[3]:
            modde["do_wellbore"] = data[3].lower() == "true"

        if data[4]:
            modde["two_phase_co2"] = data[4].lower() == "true"

        # Number of primary variables
        if modde["incon_type"] == "1LINE":
            n_variables = -1
        
        elif modde["incon_type"] == "2LINES":
            n_variables = -2

        elif modde["incon_type"] == "3LINES":
            n_variables = -3

        elif modde["incon_type"] == "4LINES":
            n_variables = -4

        elif modde["incon_type"] and modde["incon_type"].startswith("FM"):
            n_variables = list(map(int, list(modde["incon_type"][4:])))

        else:
            n_variables = None

        return {
            "data": self.prune_values(modde),
            "n_variables": n_variables,
            "label_length": modde["label_length"],
        }

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write MODDE block data."""
        out = []

        # Record 1
        values = [
            parameters.get("eos", "").upper(),
            parameters.get("incon_type", "").upper(),
            parameters.get("cubic_type", "").upper(),
        ]
        out += self.writers[1](values)

        # Record 2
        out += self.writers[2]([parameters.get("label_length")])

        # Record 3
        values = [
            parameters.get("isothermal"),
            parameters.get("do_diffusion"),
            parameters.get(f"include_{self._components.get(parameters.get('eos', '').lower(), '')}"),
            parameters.get("do_wellbore"),
            parameters.get("two_phase_co2"),
        ]
        values[0] = not values[0] if values[0] is not None else None
        values = [str(value).lower() if value is not None else "" for value in values]
        out += self.writers[3](values)

        return out

    def _write_conditions(self, parameters: dict, simulator: str, *args, **kwargs) -> bool:
        """Check if MODDE block should be written."""
        return bool(parameters.get("eos")) and simulator == "tough4"

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a MODDE block."""
        parameters.update(data["data"])
