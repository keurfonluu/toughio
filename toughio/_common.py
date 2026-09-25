from __future__ import annotations

import os
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from io import TextIOWrapper
from typing import Any, Literal, Optional

import numpy as np


def str2format(fmt: str) -> Sequence[str]:
    """Convert a string to a list of formats."""
    token_to_format = {
        "s": "",
        "S": "",
        "d": "g",
        "f": "f",
    }

    base_fmt = "{{:{}}}"
    out = [
        (
            base_fmt.format(f"{token[:-1]}.{token[:-1]}")
            if token[-1].lower() == "s"
            else base_fmt.format(f">{token[:-1]}{token_to_format[token[-1]]}")
        )
        for token in fmt.split(",")
    ]

    return out


def get_label_length(label: str) -> int:
    """Get length of cell label."""
    label_length = 5
    while label_length < len(label) and label[label_length].isdigit():
        label_length += 1

    return max(min(label_length, 9), 5)


def register_format(
    fmt: str,
    ext_to_fmt: dict,
    reader_map: dict,
    writer_map: dict,
    extensions: Sequence[str],
    reader: Optional[Callable] = None,
    writer: Optional[Callable] = None,
) -> None:
    """Register a new format."""
    for ext in extensions:
        ext_to_fmt[ext] = fmt

    if reader is not None:
        reader_map[fmt] = reader

    if writer is not None:
        writer_map[fmt] = writer


def filetype_from_filename(
    filename: str,
    ext_to_fmt: dict,
    default: str = "",
) -> str:
    """Determine file type from its extension."""
    if not isinstance(filename, TextIOWrapper):
        ext = os.path.splitext(filename)[1].lower()

        return ext_to_fmt[ext] if ext in ext_to_fmt else default

    else:
        return default


@contextmanager
def open_file(
    path_or_buffer: str | os.PathLike | TextIOWrapper, mode: Literal["r", "w"]
) -> Iterator[TextIOWrapper]:
    """Open file or buffer."""

    def is_buffer(obj: Any, mode: Literal["r", "w"]) -> bool:
        return ("r" in mode and hasattr(obj, "read")) or (
            "w" in mode and hasattr(obj, "write")
        )

    if is_buffer(path_or_buffer, mode):
        yield path_or_buffer

    else:
        with open(path_or_buffer, mode) as f:
            yield f


def prune_values(
    data: dict | Sequence[float], value: Optional[float] = None
) -> dict | Sequence[float]:
    """Remove values from dict or trailing values from list."""
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v != value}

    elif isinstance(data, (list, tuple, np.ndarray)):
        return [x for i, x in enumerate(data) if any(xx != value for xx in data[i:])]

    else:
        return data
