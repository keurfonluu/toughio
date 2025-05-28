from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class TIMBC(DataBlock):
    name = "TIMBC"
    formats = {
        0: "5d,5s",
        "1/tough": "10s",
        "1/tough3": "10s",
        "1/tough4": "10s,5d,5d",  
        2: "5d,5d",
        3: "10f,10f",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        simulator: str,
    ) -> dict:
        """Read TIMBC block data."""
        timbc = {"boundary_conditions": []}

        # Record 1
        data = self.readers[0](f)
        ntptab = data[0]

        for _ in range(ntptab):
            # Records 2 and 3
            if simulator == "tough4":
                data = self.readers[f"1/{simulator}"](f)

            else:
                tmp2 = self.readers[2](f)
                tmp1 = self.readers[f"1/{simulator}"](f)
                data = tmp1 + tmp2
            
            if len(data) < 2:
                raise ValueError()

            nbcp = data[1]
            nbcpv = data[2]
            bcelm = data[0]

            # Record 4
            times, values = [], []

            for _ in range(nbcp):
                data = self.readers[3](f)
                times.append(data[0])
                values.append(data[1])

            tmp = {
                "label": bcelm,
                "variable": nbcpv,
                "times": times,
                "values": values,
            }
            timbc["boundary_conditions"].append(tmp)

        return timbc

    def _write(
        self,
        parameters: dict,
        simulator: str,
        *args,
        **kwargs,
    ) -> list[str]:
        """Write TIMBC block data."""
        out = []

        # Record 1
        ntptab = len(parameters.get("boundary_conditions", []))
        out += self.writers[0]([ntptab])

        for data in parameters.get("boundary_conditions"):
            # Times
            times = data.get("times", [])
            values = data.get("values", [])
            nbcp = len(times)

            if len(values) < nbcp:
                raise ValueError()

            # Record 2
            if simulator == "tough4":
                out += self.writers[f"1/{simulator}"]([data["label"], nbcp, data["variable"]])

            else:
                # Record 3
                out += self.writers[2]([nbcp, data["variable"]])
                out += self.writers[f"1/{simulator}"]([data["label"]])

            # Record 4
            for time, value in zip(times, values):
                out += self.writers[3]([time, value])

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if TIMBC block should be written."""
        return len(parameters.get("boundary_conditions", [])) > 0
