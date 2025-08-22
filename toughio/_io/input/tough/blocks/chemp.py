from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class CHEMP(DataBlock):
    name = "CHEMP"
    formats = {
        1: "5d",
        2: "20s",
        3: ",".join(5 * ["10f"]),
    }

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read CHEMP block data."""
        chemp = {"chemical_properties": {}}

        # Record 1
        data = self.readers[1](f)
        n = data[0]

        # Record 2
        for _ in range(n):
            tmp = {}

            data = self.readers[2](f)
            chem = data[0]

            data = self.readers[3](f)
            tmp["temperature_crit"] = data[0]
            tmp["pressure_crit"] = data[1]
            tmp["compressibility_crit"] = data[2]
            tmp["pitzer_factor"] = data[3]
            tmp["dipole_moment"] = data[4]

            data = self.readers[3](f)
            tmp["boiling_point"] = data[0]
            tmp["vapor_pressure_a"] = data[1]
            tmp["vapor_pressure_b"] = data[2]
            tmp["vapor_pressure_c"] = data[3]
            tmp["vapor_pressure_d"] = data[4]

            data = self.readers[3](f)
            tmp["molecular_weight"] = data[0]
            tmp["heat_capacity_a"] = data[1]
            tmp["heat_capacity_b"] = data[2]
            tmp["heat_capacity_c"] = data[3]
            tmp["heat_capacity_d"] = data[4]

            data = self.readers[3](f)
            tmp["napl_density_ref"] = data[0]
            tmp["napl_temperature_ref"] = data[1]
            tmp["gas_diffusivity_ref"] = data[2]
            tmp["gas_temperature_ref"] = data[3]
            tmp["exponent"] = data[4]

            data = self.readers[3](f)
            tmp["napl_viscosity_a"] = data[0]
            tmp["napl_viscosity_b"] = data[1]
            tmp["napl_viscosity_c"] = data[2]
            tmp["napl_viscosity_d"] = data[3]
            tmp["volume_crit"] = data[4]

            data = self.readers[3](f)
            tmp["solubility_a"] = data[0]
            tmp["solubility_b"] = data[1]
            tmp["solubility_c"] = data[2]
            tmp["solubility_d"] = data[3]

            data = self.readers[3](f)
            tmp["oc_coeff"] = data[0]
            tmp["oc_fraction"] = data[1]
            tmp["oc_decay"] = data[2]

            chemp["chemical_properties"][chem] = tmp

        return chemp

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write CHEMP block data."""
        data = parameters["chemical_properties"]

        # Record 1
        out = self.writers[1]([len(data)])

        # Record 2
        for k, v in data.items():
            out += self.writers[2]([k])

            values = [
                v.get(key)
                for key in [
                    "temperature_crit",
                    "pressure_crit",
                    "compressibility_crit",
                    "pitzer_factor",
                    "dipole_moment",
                ]
            ]
            out += self.writers[3](values)

            values = [
                v.get(key)
                for key in [
                    "boiling_point",
                    "vapor_pressure_a",
                    "vapor_pressure_b",
                    "vapor_pressure_c",
                    "vapor_pressure_d",
                ]
            ]
            out += self.writers[3](values)

            values = [
                v.get(key)
                for key in [
                    "molecular_weight",
                    "heat_capacity_a",
                    "heat_capacity_b",
                    "heat_capacity_c",
                    "heat_capacity_d",
                ]
            ]
            out += self.writers[3](values)

            values = [
                v.get(key)
                for key in [
                    "napl_density_ref",
                    "napl_temperature_ref",
                    "gas_diffusivity_ref",
                    "gas_temperature_ref",
                    "exponent",
                ]
            ]
            out += self.writers[3](values)

            values = [
                v.get(key)
                for key in [
                    "napl_viscosity_a",
                    "napl_viscosity_b",
                    "napl_viscosity_c",
                    "napl_viscosity_d",
                    "volume_crit",
                ]
            ]
            out += self.writers[3](values)

            values = [
                v.get(key)
                for key in [
                    "solubility_a",
                    "solubility_b",
                    "solubility_c",
                    "solubility_d",
                ]
            ]
            out += self.writers[3](values)

            values = [
                v.get(key)
                for key in [
                    "oc_coeff",
                    "oc_fraction",
                    "oc_decay",
                ]
            ]
            out += self.writers[3](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if CHEMP block should be written."""
        return bool(parameters.get("chemical_properties", {}))
