from __future__ import annotations

from collections.abc import Sequence
from typing import TextIO

import numpy as np

from .....core import DataBlock, FileIterator, RecordFormatter


class MESHM(DataBlock):
    name = "MESHM"
    formats = {
        0: "5s",
        "1/XYZ": "10f",
        "2/XYZ": "5s,5d,10f",
        "3/XYZ": ",".join(8 * ["10f"]),
        "1/RZ2D": "5s",
        "1/RZ2D/RADII": "5d",
        "2/RZ2D/RADII": ",".join(8 * ["10f"]),
        "1/RZ2D/EQUID": "5d,5s,10f",
        "1/RZ2D/LOGAR": "5d,5s,10f,10f",
        "1/RZ2D/LAYER": "5d",
        "2/RZ2D/LAYER": ",".join(8 * ["10f"]),
        "1/MINC": "5s,5s,5s,5s",
        "2/MINC": "3d,3d,4s,10f,10f,10f,10f,10f,10f,10f",
        "3/MINC": ",".join(8 * ["10f"]),
    }
    multiples = {"3/XYZ", "2/RZ2D/RADII", "2/RZ2D/LAYER", "3/MINC"}
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read MESHM block data."""
        # Mesh type
        data = self.readers[0](f)
        mesh_type = data[0].upper()

        if mesh_type in {"XYZ", "RZ2D", "RZ2DL"}:
            meshm = {"meshmaker": {"type": mesh_type.lower()}}

        else:
            meshm = {"minc": {}}

        # XYZ
        if mesh_type == "XYZ":
            # Record 1
            data = self.readers["1/XYZ"](f)
            meshm["meshmaker"]["angle"] = data[0]

            # Record 2
            meshm["meshmaker"]["parameters"] = []

            while True:
                line = f.next()

                if line.strip():
                    data = self.readers["2/XYZ"](line)
                    tmp = {
                        "type": data[0].lower(),
                        "n_increment": data[1],
                    }

                    if len(data) > 2 and data[2]:
                        tmp["sizes"] = data[2]

                    else:
                        sizes = []

                        while len(sizes) < tmp["n_increment"]:
                            data = self.readers["3/XYZ"](f)
                            sizes += self.prune_values(data)

                        tmp["sizes"] = sizes[: tmp["n_increment"]]

                    meshm["meshmaker"]["parameters"].append(tmp)

                else:
                    break

        # RZ2D
        elif mesh_type in {"RZ2D", "RZ2DL"}:
            # Record 1
            meshm["meshmaker"]["parameters"] = []

            while True:
                line = f.next()

                if line.strip():
                    data = self.readers["1/RZ2D"](line)
                    data_type = data[0].upper()

                    if data_type == "RADII":
                        data = self.readers["1/RZ2D/RADII"](f)
                        n = data[0]
                        radii = []

                        while len(radii) < n:
                            data = self.readers["2/RZ2D/RADII"](f)
                            radii += self.prune_values(data)

                        tmp = {
                            "type": data_type.lower(),
                            "radii": radii[:n],
                        }
                        meshm["meshmaker"]["parameters"].append(tmp)

                    elif data_type == "EQUID":
                        data = self.readers["1/RZ2D/EQUID"](f)
                        tmp = {
                            "type": data_type.lower(),
                            "n_increment": data[0],
                            "size": data[2],
                        }
                        meshm["meshmaker"]["parameters"].append(tmp)

                    elif data_type == "LOGAR":
                        data = self.readers["1/RZ2D/LOGAR"](f)
                        tmp = {
                            "type": data_type.lower(),
                            "n_increment": data[0],
                            "radius": data[2],
                            "radius_ref": data[3],
                        }
                        meshm["meshmaker"]["parameters"].append(tmp)

                    elif data_type == "LAYER":
                        # Record 1
                        data = self.readers["1/RZ2D/LAYER"](f)
                        n = data[0]

                        # Record 2
                        thicknesses = []

                        while len(thicknesses) < n:
                            data = self.readers["2/RZ2D/LAYER"](f)
                            thicknesses += self.prune_values(data)

                        tmp = {"type": data_type.lower(), "thicknesses": thicknesses[:n]}
                        meshm["meshmaker"]["parameters"].append(tmp)

                        # LAYER closes the block RZ2D
                        # RZ2D can be followed by MINC
                        line = f.next()

                        if line.startswith("MINC"):
                            meshm["minc"] = self._read_minc(f)

                        else:
                            break

                else:
                    break

        # MINC
        elif mesh_type == "MINC":
            meshm["minc"] = self._read_minc(f)

        return meshm

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write MESHM block data."""
        out = []
        data = parameters.get("meshmaker", {})

        if data:
            # Mesh type
            mesh_type = data.get("type", "").upper()
            out += self.writers[0]([mesh_type])

            # XYZ
            if mesh_type == "XYZ":
                # Record 1
                out += self.writers["1/XYZ"]([data.get("angle")])

                # Record 2
                for v in data["parameters"]:
                    values = [v.get("type", "").upper()]
                    ndim = np.ndim(v.get("sizes", []))

                    if ndim == 0:
                        values += [
                            v.get("n_increment"),
                            v.get("sizes"),
                        ]
                        out += self.writers["2/XYZ"](values)

                    elif ndim == 1:
                        values += [v.get("n_increment", len(v.get("sizes", [])))]
                        out += self.writers["2/XYZ"](values)
                        out += self.writers["3/XYZ"](v.get("sizes", []))

                    else:
                        raise ValueError()

                # Blank record
                out += ["\n"]

            # RZ2D
            elif mesh_type in {"RZ2D", "RZ2DL"}:
                for v in data["parameters"]:
                    parameter_type = v.get("type", "").upper()
                    out += self.writers["1/RZ2D"]([parameter_type])

                    if parameter_type == "RADII":
                        radii = v.get("radii", [])
                        out += self.writers["1/RZ2D/RADII"]([len(radii)])
                        out += self.writers["2/RZ2D/RADII"](radii)

                    elif parameter_type == "EQUID":
                        values = [
                            v.get("n_increment"),
                            None,
                            v.get("size"),
                        ]
                        out += self.writers["1/RZ2D/EQUID"](values)

                    elif parameter_type == "LOGAR":
                        values = [
                            v.get("n_increment"),
                            None,
                            v.get("radius"),
                            v.get("radius_ref"),
                        ]
                        out += self.writers["1/RZ2D/LOGAR"](values)

                    elif parameter_type == "LAYER":
                        thicknesses = v.get("thicknesses", [])
                        out += self.writers["1/RZ2D/LAYER"]([len(thicknesses)])
                        out += self.writers["2/RZ2D/LAYER"](thicknesses)

        if parameters.get("minc"):
            out += self._write_minc(parameters)

        return out

    def _read_minc(self, f: FileIterator | TextIO | str) -> dict:
        """Read MINC data."""
        minc = {}

        # Record 1
        data = self.readers["1/MINC"](f)
        minc["type"] = data[1].lower()
        minc["dual"] = data[3].lower()

        # Record 2
        data = self.readers["2/MINC"](f)
        minc["n_minc"] = data[0]
        n_volume = data[1]
        minc["where"] = data[2].lower()
        minc["parameters"] = self.prune_values(data[3:])

        # Record 3
        minc["volumes"] = []

        while len(minc["volumes"]) < n_volume:
            data = self.readers["3/MINC"](f)
            minc["volumes"] += self.prune_values(data)

        return minc

    def _write_minc(self, parameters: dict) -> list[str]:
        """Write MINC data."""
        data = parameters["minc"]
        volumes = data.get("volumes", [])
        
        # Mesh type
        out = self.writers[0](["MINC"])

        # Record 1
        values = [
            "PART",
            data.get("type", "").upper(),
            None,
            data.get("dual", "").upper(),
        ]
        out += self.writers["1/MINC"](values)

        # Record 2
        values = [
            data.get("n_minc"),
            len(volumes),
            f"{data.get('where', '').upper():<4}",
            *data.get("parameters", []),
        ]
        out += self.writers["2/MINC"](values)

        # Record 3
        out += self.writers["3/MINC"](volumes)

        return out

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if MESHM block should be written."""
        return parameters.get("meshmaker", {}) or parameters.get("minc", {})
