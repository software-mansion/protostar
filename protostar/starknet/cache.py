import os
from os import path
from typing import Optional
import json
from pathlib import Path


class CacheUtil:
    _CACHE_DIR_NAME = ".protostar_cache"

    def __init__(self, project_path: str):
        self._cache_path = path.join(project_path, self._CACHE_DIR_NAME)
        if not path.exists(self._cache_path):
            os.mkdir(self._cache_path)

    def persist(self, name: str, value: dict, override=True) -> None:
        if not override and self.obtain(name):
            return

        file_path = path.join(self._cache_path, name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(value))

    def obtain(self, name: str) -> Optional[dict]:
        if not path.exists(self._cache_path):
            return None
        file_path = path.join(self._cache_path, name)
        if not path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as file:
            if file_contents := file.read():
                return json.loads(file_contents)
        return None
