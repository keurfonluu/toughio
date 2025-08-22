from __future__ import annotations

from typing import TextIO

from .....core import DataBlock, FileIterator


class END_COMMENTS(DataBlock):
    name = "END COMMENTS"
    formats = {}

    def __init__(self, *args, **kwargs):
        """Initialize END_COMMENTS block."""
        super().__init__(*args, **kwargs)
        self._space_between_blocks = False

    def _read(self, f: FileIterator | TextIO | str, *args, **kwargs) -> dict:
        """Read END COMMENTS block data."""
        # Save end comments
        end_comments = []

        while True:
            try:
                end_comments.append(f.next().rstrip())

            except StopIteration:
                break

        # Remove trailing empty records
        end_comments = [comment if comment else None for comment in end_comments]
        end_comments = self.prune_values(end_comments)
        end_comments = [comment if comment else "" for comment in end_comments]

        return {"end_comments": end_comments} if end_comments else {}

    def _write(self, parameters: dict, *args, **kwargs) -> list[str]:
        """Write END COMMENTS block data."""
        end_comments = parameters.get("end_comments", [])
        end_comments = [end_comments] if isinstance(end_comments, str) else end_comments

        return [f"{comment}\n" for comment in end_comments]

    def _write_header(self) -> str:
        """Write END COMMENTS block header."""
        return ""

    def _write_conditions(self, parameters: dict, *args, **kwargs) -> bool:
        """Check if END COMMENTS block should be written."""
        return bool(parameters.get("end_comments", []))

    def update(
        self,
        parameters: dict,
        data: dict,
    ) -> None:
        """Update input file parameters given a END COMMENTS block."""
        end_comments = data.get("end_comments", [])

        if len(end_comments) == 1:
            end_comments = end_comments[0]

        if end_comments:
            parameters["end_comments"] = end_comments
