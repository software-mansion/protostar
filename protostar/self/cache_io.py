from typing import Optional
import json
from pathlib import Path


class CacheIO:
    _CACHE_DIR_NAME = ".protostar_cache"
    _EXTENSION = ".json"

    def __init__(self, project_root_path: Path):
        self._cache_path = project_root_path / Path(self._CACHE_DIR_NAME)
        self._cache_path.mkdir(exist_ok=True)
        self._gitignore_path = Path(self._cache_path / ".gitignore")
        self._gitignore_checked = False

    def write(self, name: str, value: dict) -> None:
        if not self._gitignore_path.exists():
            self._gitignore_path.write_text("*\n", encoding="utf-8")
        Path(self._cache_path / (name + self._EXTENSION)).write_text(
            json.dumps(value), encoding="utf-8"
        )

    def read(self, name: str) -> Optional[dict]:
        if not self._cache_path.exists():
            return None
        file_path = self._cache_path / (name + self._EXTENSION)
        if not file_path.exists():
            return None

        if file_contents := Path(file_path, encodings="utf-8").read_text(
            encoding="utf-8"
        ):
            return json.loads(file_contents)

        return None
