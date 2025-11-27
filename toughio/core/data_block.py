from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

import numpy as np

from .file import FileIterator
from .record_formatter import RecordFormatter

if TYPE_CHECKING:
    from typing import Any, Optional, TextIO


class DataBlock:
    """
    Data block class.

    Parameters
    ----------
    space_between_blocks : bool, default False
        If True, add an empty record between blocks.
    space_between_values : bool, default False
        If True, add a white space between floating point values.
    free_format : bool, default False
        If True, write comma-separated free-format records.
    delimiter : str, default ','
        Delimiter for free-format records.

    """

    __name__: str = "DataBlock"
    __qualname__: str = "toughio.DataBlock"

    name: str
    formats: dict
    multiples: set = set()  # Flag for record formatters that write multiple records
    _format: str
    _space_between_blocks: bool = False

    def __init__(
        self,
        space_between_values: bool = False,
        space_between_blocks: bool = False,
        free_format: bool = False,
        delimiter: str = ",",
    ) -> None:
        """Initialize a data block."""
        self._space_between_values = space_between_values
        self._space_between_blocks = self._space_between_blocks or space_between_blocks
        self._free_format = free_format
        self._delimiter = delimiter

    def read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read a data block."""
        if not hasattr(self, "readers"):
            self.readers = {
                k: RecordFormatter(
                    v,
                    mode="r",
                    free_format=self.free_format,
                    delimiter=self.delimiter,
                )
                for k, v in self.formats.items()
            }

        return self._read(f, *args, **kwargs)

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a data block."""
        parameters.update(data)

    def write(self, parameters: Optional[dict] = None, *args, **kwargs) -> list[str]:
        """Write a data block."""
        if not self._write_conditions(parameters, *args, **kwargs):
            return []

        if not hasattr(self, "writers"):
            self.writers = {
                k: RecordFormatter(
                    v,
                    mode="w",
                    free_format=self.free_format,
                    space_between_values=self.space_between_values,
                    multiple=k in self.multiples,
                    delimiter=self.delimiter,
                )
                for k, v in self.formats.items()
            }

        out = [self._write_header()]
        out += self._write(parameters, *args, **kwargs)
        out += ["\n"] if self.space_between_blocks else []

        return out

    def _write_header(self) -> str:
        """Write header for data block."""
        end = (
            "----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8"
            if not self.free_format
            else "-" * 75
        )

        return f"{self.name:<5s}{end}\n"

    @staticmethod
    def get_label_length(label: str) -> int:
        """Get label length from label string."""
        from .._common import get_label_length

        return get_label_length(label)

    @staticmethod
    def prune_values(
        data: dict | Sequence[Any],
        value: Optional[float] = None,
    ) -> dict | Sequence[float]:
        """Remove values from dict or trailing values from list."""
        from .._common import prune_values

        return prune_values(data, value)

    def read_model_record(
        self,
        f: FileIterator | TextIO | str,
        reader: RecordFormatter,
        i: int = 2,
    ) -> dict:
        """Read model record defined by 'id' and 'parameters'."""
        data = reader(f)

        return {
            "id": data[0],
            "parameters": self.prune_values(data[i:]),
        }

    @staticmethod
    def read_primary_variables(
        f: FileIterator,
        reader: RecordFormatter,
        n_variables: int | Sequence[int],
    ) -> list[Any]:
        """Read primary variables."""
        data = []

        if n_variables:
            if not isinstance(n_variables, int):
                n_variables = len(n_variables)

            n = (
                -n_variables
                if n_variables < 0
                else int(np.ceil(n_variables / len(reader.format)))
            )

            for _ in range(n):
                data += reader(f)

        else:
            while True:
                i = f.tell()
                line = f.next()

                if line.strip():
                    try:
                        data += reader(line)

                    except ValueError:
                        break

                else:
                    break

            f.seek(i, increment=-1)

        return data

    @staticmethod
    def write_model_record(
        data: dict,
        key: str,
        writer: RecordFormatter,
    ) -> list[str]:
        """Write model record defined by 'id' and 'parameters'."""
        if key in data:
            values = [data[key]["id"]]

            if not writer.free_format:
                values.append(None)

            values += list(data[key]["parameters"])

        else:
            values = []

        return writer(values)

    @abstractmethod
    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict: ...

    @abstractmethod
    def _write(self, parameters: Optional[dict] = None, *args, **kwargs) -> list[str]: ...

    def _write_conditions(self, parameters: Optional[dict] = None, *args, **kwargs) -> bool:
        """Write conditions for a data block."""
        return True

    @property
    def format(self) -> str:
        """Return format string."""
        return self._format

    @property
    def free_format(self) -> bool:
        """Return True if free format."""
        return self._free_format

    @free_format.setter
    def free_format(self, value: bool) -> None:
        """Set free format flag."""
        self._free_format = value

    @property
    def delimiter(self) -> str:
        """Return delimiter string."""
        return self._delimiter

    @delimiter.setter
    def delimiter(self, value: str) -> None:
        """Set delimiter string."""
        self._delimiter = value

    @property
    def space_between_blocks(self) -> bool:
        """Return True if space between blocks."""
        return self._space_between_blocks

    @space_between_blocks.setter
    def space_between_blocks(self, value: bool) -> None:
        """Set space between blocks flag."""
        self._space_between_blocks = value

    @property
    def space_between_values(self) -> bool:
        """Return True if space between values."""
        return self._space_between_values

    @space_between_values.setter
    def space_between_values(self, value: bool) -> None:
        """Set space between values flag."""
        self._space_between_values = value
