from datetime import datetime as DateTime
from pathlib import Path
from typing import Optional


class MigratorDateTimeState:
    def __init__(self, migration_file_path: Path) -> None:
        self._migration_file_path = migration_file_path
        self._datetime: Optional[DateTime] = None

    def update_to_now(self):
        self._datetime = DateTime.now()

    def get_output_stem(self) -> Optional[str]:
        assert self._datetime is not None
        migration_file_stem = self._migration_file_path.stem
        prefix = DateTime.strftime(self._datetime, "%Y%m%d%H%M%S")
        return f"{prefix}_{migration_file_stem}"
