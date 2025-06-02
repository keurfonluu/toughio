from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class FLAC(DataBlock):
    name = "FLAC"
    formats = {
        1: ",".join(16 * ["5d"]),
        2: "10d,10f,10f,10f,10f,10f,10f,10f",
        3: "5d,5s,10f,10f,10f,10f,10f,10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        parameters: dict,
        *args,
        **kwargs
    ) -> dict:
        """Read FLAC block data."""
        flac = {"flac": {}}

        # Record 1
        data = self.readers[1](f)
        flac["flac"]["creep"] = data[0]
        flac["flac"]["porosity_model"] = data[1]
        flac["flac"]["version"] = data[2]

        # Additional records
        for rock in parameters["rocks"]:
            parameters["rocks"][rock]["permeability_model"] = self.read_model_record(f, self.readers[2], 1)
            parameters["rocks"][rock]["equivalent_pore_pressure"] = self.read_model_record(f, self.readers[3], 2)

        flac["flac"] = self.prune_values(flac["flac"])

        return flac

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write FLAC block data."""
        # Record 1
        values = [
            bool(parameters["flac"].get("creep", False)),
            parameters["flac"].get("porosity_model"),
            parameters["flac"].get("version"),
        ]
        out = self.writers[1](values)

        # Additional records
        for v in parameters["rocks"].values():
            data = parameters.get("default", {}).copy()
            data.update(v)

            # Permeability model
            values = [data.get("permeability_model", {}).get("id", 1)]
            values += list(data.get("permeability_model", {}).get("parameters", []))
            out += self.writers[2](values)

            # Equivalent pore pressure
            values = [data.get("equivalent_pore_pressure", {}).get("id", 3), None]
            values += list(data.get("equivalent_pore_pressure", {}).get("parameters", []))
            out += self.writers[3](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if FLAC block should be written."""
        return bool(parameters.get("flac", {}))

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a FLAC block."""
        parameters["flac"] = data["flac"]
