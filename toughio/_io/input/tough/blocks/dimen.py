from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class DIMEN(DataBlock):
    name = "DIMEN"
    formats = {1: ",".join(8 * ["10d"])}
    multiples = {1}

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read DIMEN block data."""
        dimen = {"array_dimensions": {}}

        # Record 1
        data = self.readers[1](f)
        dimen["array_dimensions"].update(
            {
                "n_rocks": data[0],
                "n_times": data[1],
                "n_generators": data[2],
                "n_rates": data[3],
                "n_increment_x": data[4],
                "n_increment_y": data[5],
                "n_increment_z": data[6],
                "n_increment_rad": data[7],
            }
        )

        # Record 2
        data = self.readers[1](f)
        dimen["array_dimensions"].update(
            {
                "n_properties": data[0],
                "n_properties_times": data[1],
                "n_regions": data[2],
                "n_regions_parameters": data[3],
                "n_ltab": data[4],
                "n_rpcap": data[5],
                "n_elements_timbc": data[6],
                "n_timbc": data[7],
            }
        )

        return dimen

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write DIMEN block data."""
        values = [
            parameters["array_dimensions"].get(key) for key in [
                "n_rocks",
                "n_times",
                "n_generators",
                "n_rates",
                "n_increment_x",
                "n_increment_y",
                "n_increment_z",
                "n_increment_rad",
                "n_properties",
                "n_properties_times",
                "n_regions",
                "n_regions_parameters",
                "n_ltab",
                "n_rpcap",
                "n_elements_timbc",
                "n_timbc",
            ]
        ]
        out = self.writers[1](values)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if DIMEN block should be written."""
        return bool(parameters.get("array_dimensions", {}))
