from __future__ import annotations

from typing import Optional, TextIO

from .....core import DataBlock, FileIterator


class INDOM(DataBlock):
    name = "INDOM"
    formats = {
        0: ",".join(4 * ["20f"]),
        5: "5s,5d",
    }
    multiples = {0}
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        n_variables: int,
        eos: Optional[str] = None,
    ) -> dict:
        """Read INDOM block data."""
        indom = {"rocks": {}}

        # Read records
        line = f.next()

        while True:
            if line.strip():
                # Record 1
                data = self.readers[5](line)
                rock = data[0]
                phase_composition = data[1]  # ECO2M, TMVOC

                # Record 2
                data = self.read_primary_variables(f, self.readers[0], n_variables)
                data = self.prune_values(data)
                indom["rocks"][rock] = {"initial_condition": data}

                if not n_variables:
                    n_variables = len(data)

                if eos in {"eco2m", "tmvoc"}:
                    indom["rocks"][rock]["phase_composition"] = phase_composition

            else:
                break

            line = f.next()

        return {
            "data": indom,
            "n_variables": n_variables,
        }

    def _write(self, parameters: dict, eos: str, *args, **kwargs) -> list[str]:
        """Write INDOM block data."""
        # Write records
        out = []

        for k, v in parameters["rocks"].items():
            cond1 = "initial_condition" in v
            cond2 = (
                eos in {"eco2m", "tmvoc"}
                and "phase_composition" in v
                and v["phase_composition"] is not None
            )

            if cond1 or cond2:
                # Record 1
                values = [k]

                if eos in {"eco2m", "tmvoc"}:
                    values.append(v["phase_composition"])

                else:
                    values.append(None)

                out += self.writers[5](values)

                if cond1:
                    out += self.writers[0](v["initial_condition"])

                else:
                    out += ["\n"]

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if INDOM block should be written."""
        indom = False

        for rock in parameters.get("rocks", {}).values():
            if "initial_condition" in rock:
                if any(x is not None for x in rock["initial_condition"][:4]):
                    indom = True
                    break

        return indom
