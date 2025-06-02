from __future__ import annotations

from collections.abc import Sequence
from typing import TextIO

from .....core import DataBlock, FileIterator, RecordFormatter


def _read_oft(
    f: FileIterator | TextIO | str,
    oft: str,
    label_length: int,
    readers: Sequence[RecordFormatter],
) -> dict:
    """Read FOFT, COFT and GOFT blocks data."""
    from ....._common import get_label_length

    key = oft_to_key[oft]
    history = {key: []}

    # Label length
    line = f.next()

    if not label_length:
        label_length = get_label_length(line[:9])

    label_format = f"{{:>{label_length if oft != 'COFT' else 2 * label_length}}}"
    iflag = 2 if oft != "GOFT" else 3

    # Read records
    while True:
        if line.strip():
            data = readers[label_length](line)
            tmp = {"label": label_format.format(data[0])}

            if data[iflag] is not None:
                tmp["flag"] = data[iflag]

            history[key].append(tmp)

        else:
            break

        line = f.next()

    return {
        "data": history,
        "label_length": label_length,
    }


def _write_oft(
    oft: str,
    parameters: dict,
    writers: Sequence[RecordFormatter],
) -> list[str]:
    """Write FOFT, COFT, and GOFT blocks data."""
    out = []

    for v in parameters[oft_to_key[oft]]:
        data = v if isinstance(v, dict) else {"label": v }

        values = [data.get("label", "")]
        values += [None] if oft != "GOFT" else [None, None]
        values += [data.get("flag")]
        out += writers[max(len(values[0]) // (2 if oft == "COFT" else 1), 5)](values)

    return out


class FOFT(DataBlock):
    name = "FOFT"
    formats = {
        5: "5s,5s,5d",
        6: "6s,4s,5d",
        7: "7s,3s,5d",
        8: "8s,2s,5d",
        9: "9s,1s,5d",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        *args,
        **kwargs
    ) -> dict:
        """Read FOFT block data."""
        return _read_oft(f, "FOFT", label_length, self.readers)

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write FOFT block data."""
        return _write_oft("FOFT", parameters, self.writers)

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if FOFT block should be written."""
        return len(parameters.get("element_history", {})) > 0

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a FOFT block."""
        parameters.update(data["data"])


class COFT(DataBlock):
    name = "COFT"
    formats = {
        5: "10s,10s,5d",
        6: "12s,8s,5d",
        7: "14s,6s,5d",
        8: "16s,4s,5d",
        9: "18s,2s,5d",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        *args,
        **kwargs
    ) -> dict:
        """Read COFT block data."""
        return _read_oft(f, "COFT", label_length, self.readers)

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write COFT block data."""
        return _write_oft("COFT", parameters, self.writers)

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if COFT block should be written."""
        return len(parameters.get("connection_history", {})) > 0

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a COFT block."""
        parameters.update(data["data"])


class GOFT(DataBlock):
    name = "GOFT"
    formats = {
        5: "5s,5s,5s,5d",
        6: "6s,4s,5s,5d",
        7: "7s,3s,5s,5d",
        8: "8s,2s,5s,5d",
        9: "9s,1s,5s,5d",
    }
    _space_between_blocks = True

    def _read(
        self,
        f: FileIterator | TextIO | str,
        label_length: int,
        *args,
        **kwargs
    ) -> dict:
        """Read GOFT block data."""
        return _read_oft(f, "GOFT", label_length, self.readers)

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write GOFT block data."""
        return _write_oft("GOFT", parameters, self.writers)

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if GOFT block should be written."""
        return len(parameters.get("generator_history", {})) > 0

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a GOFT block."""
        parameters.update(data["data"])


oft_to_key = {
    "FOFT": "element_history",
    "COFT": "connection_history",
    "GOFT": "generator_history",
}
