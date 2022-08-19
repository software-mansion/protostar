from datetime import datetime as DateTime
from pathlib import Path
from typing import Optional


class MigratorDateTimeState:
    def __init__(self, migration_file_path: Path) -> None:
        self._migration_file_path = migration_file_path
        self._datetime: Optional[DateTime] = None

    def update_to_now(self):
        self._datetime = DateTime.now()

    def _get_prefix(self) -> Optional[str]:
        assert self._datetime is not None
        return DateTime.strftime(self._datetime, "%Y%m%d%H%M%S")

    def get_compilation_output_path(self) -> Path:
        migrations_dir = self._migration_file_path.parent
        migration_stem = self._migration_file_path.stem
        prefix = self._get_prefix()
        return migrations_dir / f"{prefix}_{migration_stem}"
