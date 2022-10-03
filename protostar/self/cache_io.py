from os import path
from typing import Optional
import json
from pathlib import Path


class CacheIO:
    _CACHE_DIR_NAME = ".protostar_cache"

    def __init__(self, project_root_path: Path):
        self._cache_path = project_root_path / Path(self._CACHE_DIR_NAME)
        self._cache_path.mkdir(exist_ok=True)

    def write(self, name: str, value: dict, override=True) -> None:
        if not override and path.exists(self._cache_path):
            return

        file_path = path.join(self._cache_path, name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(value))

    def read(self, name: str) -> Optional[dict]:
        if not path.exists(self._cache_path):
            return None
        file_path = path.join(self._cache_path, name)
        if not path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as file:
            if file_contents := file.read():
                return json.loads(file_contents)
        return None
