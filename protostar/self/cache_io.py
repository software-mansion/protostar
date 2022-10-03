from typing import Optional
import json
from pathlib import Path


class CacheIO:
    _CACHE_DIR_NAME = ".protostar_cache"

    def __init__(self, project_root_path: Path):
        self._cache_path = project_root_path / Path(self._CACHE_DIR_NAME)
        self._cache_path.mkdir(exist_ok=True)

    def write(self, name: str, value: dict, override=True) -> None:
        if not override and self._cache_path.exists():
            return

        with open(self._cache_path / name, "w", encoding="utf-8") as file:
            file.write(json.dumps(value))

    def read(self, name: str) -> Optional[dict]:
        if not self._cache_path.exists():
            return None
        file_path = self._cache_path / name
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as file:
            if file_contents := file.read():
                return json.loads(file_contents)
        return None
