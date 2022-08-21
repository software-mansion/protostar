from datetime import datetime as DateTime
from pathlib import Path
from typing import Optional


class MigratorDateTimeState:
    def __init__(self, migration_file_path: Path) -> None:
        self._migration_file_path = migration_file_path
        self._datetime: Optional[DateTime] = None

    @staticmethod
    def get_datetime_prefix(datetime: DateTime):
        return DateTime.strftime(datetime, "%Y%m%d%H%M%S")

    def update_to_now(self) -> None:
        self._datetime = DateTime.now()

    def get_output_stem(self) -> str:
        assert self._datetime is not None
        migration_file_stem = self._migration_file_path.stem
        prefix = self.get_datetime_prefix(self._datetime)
        return f"{prefix}_{migration_file_stem}"

    def get_compilation_output_path(self) -> Path:
        migrations_dir_path = self._migration_file_path.parent
        return migrations_dir_path / self.get_output_stem()
