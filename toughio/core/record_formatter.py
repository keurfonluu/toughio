from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .file import FileIterator


if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Literal, Optional


class RecordFormatter:
    """
    Helper class to read/write records in a data block.

    Parameters
    ----------
    fmt : str
        Format string for the records. Each token should be separated by a comma.
    mode : {'r', 'w'}, default 'r'
        Mode of the formatter. 'r' for reading, 'w' for writing.
    free_format : bool, default False
        If True, use free format for records (comma-separated values).
    space_between_values : bool, default False
        If True, add a white space between floating point values.
    multiple : bool, default False
        If True, write multiple records in a single call.
    delimiter : str, default ','
        Delimiter for free-format records. Ignored if *free_format* is False.

    """

    __name__: str = "RecordFormatter"
    __qualname__: str = "toughio.RecordFormatter"

    def __init__(
        self,
        fmt: str,
        mode: Literal["r", "w"] = "r",
        free_format: bool = False,
        space_between_values: bool = False,
        multiple: bool = False,
        delimiter: str = ",",
    ) -> None:
        """Initialize a record formatter."""
        self._mode = mode
        self._free_format = free_format
        self._space_between_values = space_between_values
        self._multiple = multiple
        self._delimiter = delimiter

        fmt = [x.strip() for x in fmt.split(",")]

        if mode == "r":
            self._format = fmt

        else:
            self._format = [
                (
                    "{{:{}}}".format(f"{tokens[token[-1]]['format']}")
                    if free_format
                    else "{{:{}}}".format(f"{token[:-1]}.{token[:-1]}")
                    if token[-1] == "s"
                    else "{{:{}}}".format(f">{token[:-1]}.{token[:-1]}")
                    if token[-1] == "S"
                    else "{{:{}}}".format(f">{token[:-1]}{tokens[token[-1]]['format']}")
                )
                for token in fmt
            ]

            if free_format:
                self._delimiter += " " if space_between_values else ""

            else:
                self._delimiter = ""

    def __call__(
        self, arg: Optional[str | FileIterator | Sequence[Any]] = None
    ) -> str | list[str]:
        """Read or write record given format."""
        # Reader
        if self.mode == "r":
            if isinstance(arg, str):
                data = arg

            else:
                data = arg.next()

            if self.free_format or "," in data:
                # Handle comments
                data = data.replace("!", "//").split("//")[0].strip()

                # Split and strip
                if "*" in data:
                    iterables = data.split(self.delimiter)
                    data = []

                    for x in iterables:
                        if "*" in x:
                            value, n = x.split("*")
                            data += [value.strip()] * int(n)

                        else:
                            data.append(x.strip())

                else:
                    data = [x.strip() for x in data.split(self.delimiter)]

                # Pad to format length
                data.extend((len(self.format) - len(data)) * [None])

                # Loop over items
                out = [
                    None if not x else tokens[token[-1]]["converter"](x)
                    for token, x in zip(self.format, data)
                ]

            else:
                i, out = 0, []

                for token in self.format:
                    n = int(token[:-1].split(".")[0])
                    tmp = data[i : i + n].rstrip()
                    out.append(tokens[token[-1]]["converter"](tmp) if tmp else None)
                    i += n

        # Writer
        else:
            if arg is None:
                return ["\n"]

            else:
                values = arg

            if not self.multiple:
                values = [
                    self.to_str(value, fmt) for value, fmt in zip(values, self.format)
                ]
                records = [values]

            else:
                n, ncol = len(values), len(self.format)
                values = [
                    values[ncol * i : min(ncol * i + ncol, n)]
                    for i in range(int(np.ceil(n / ncol)))
                ]
                records = [
                    [self.to_str(v, fmt) for v, fmt in zip(value, self.format)]
                    for value in values
                ]

            if self.free_format:
                out = [
                    f"{self.delimiter.join(record).rstrip(self.delimiter)}\n"
                    for record in records
                ]

            else:
                out = [f"{self.delimiter.join(record)}\n" for record in records]

        return out

    def to_str(self, x: Any, fmt: str) -> str:
        """Convert variable to string."""
        from .. import scientific_notation

        x = "" if x is None else x

        if not isinstance(x, str):
            if "f" in fmt:
                if self.free_format:
                    s = f"{x:.15g}"
                    s += ".0" if "." not in s and "e" not in s else ""

                    return s

                else:
                    tmp = str(float(x))

                    n = int(fmt[3:].split("f")[0])
                    fmt = f"{{:>{n}}}"

                    if self.space_between_values:
                        n -= 1

                    if len(tmp) > n or "e" in tmp:
                        tmp = (
                            tmp[:n]
                            if 1.0 <= abs(x) < 10.0
                            else format(scientific_notation(x, n))
                        )

                    return fmt.format(tmp)

            else:
                return fmt.format(x)

        else:
            return fmt.replace("g", "").replace("f", "").format(x)

    @property
    def format(self) -> Sequence[str]:
        """Return format string."""
        return self._format

    @property
    def free_format(self) -> bool:
        """Return True if free format."""
        return self._free_format

    @property
    def mode(self) -> Literal["r", "w"]:
        """Return mode."""
        return self._mode

    @property
    def multiple(self) -> bool:
        """Return True if multiple records."""
        return self._multiple

    @property
    def delimiter(self) -> str:
        """Return delimiter string."""
        return self._delimiter

    @property
    def space_between_values(self) -> bool:
        """Return True if space between values."""
        return self._space_between_values


def to_float(s: str) -> float:
    """Convert variable string to float."""
    try:
        return float(s.replace("d", "e"))

    except ValueError:
        # It's probably something like "0.0001-001"
        significand, exponent = s[:-4], s[-4:]

        return float(f"{significand}e{exponent}")


tokens = {
    "s": {"converter": str, "format": ""},  # left-justified string (default)
    "S": {"converter": str, "format": ""},  # right-justified string
    "d": {"converter": int, "format": "g"},
    "f": {"converter": to_float, "format": "f"},
    "e": {"converter": to_float, "format": "f"},
}
