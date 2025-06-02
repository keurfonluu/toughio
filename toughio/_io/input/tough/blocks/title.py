from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class TITLE(DataBlock):
    name = "TITLE"
    formats = {}

    def __init__(self, *args, **kwargs):
        """Initialize TITLE block."""
        super().__init__(*args, **kwargs)
        self._space_between_blocks = False

    def _read(
        self,
        f: FileIterator | TextIO | str,
        *args,
        **kwargs
    ) -> dict:
        """Read TITLE block data."""
        from . import registered_blocks

        title = []
        blocks = set([block.name for block in registered_blocks])

        while True:
            if len(title) >= 100:
                raise ValueError()

            line = f.readline().strip()

            if line[:5].rstrip().upper() not in blocks:
                title.append(line)

            else:
                break

        if title:
            title = title[0] if len(title) == 1 else title

        f.seek(0)

        return {"title": title}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write TITLE block data."""
        title = parameters.get("title", "")
        title = [title] if isinstance(title, str) else title

        return [f"{x:80}\n" for x in title]

    def _write_header(self) -> str:
        """Write TITLE block header."""
        return ""
