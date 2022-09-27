import os
from os import path
from typing import Optional
import json
from pathlib import Path

_CACHE_DIR_NAME = ".protostar_cache"


def _obtain_cache_path(project_path: Path):
    return path.join(project_path, _CACHE_DIR_NAME)


def persist(project_path: Path, name: str, value: dict, override=True):
    cache_path = _obtain_cache_path(project_path)
    if not path.exists(cache_path):
        os.mkdir(cache_path)

    if not override and obtain(project_path, name):
        return

    file_path = path.join(cache_path, name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(json.dumps(value))


def obtain(project_path: Path, name: str) -> Optional[dict]:
    cache_path = _obtain_cache_path(project_path)
    if not path.exists(cache_path):
        return None
    file_path = path.join(cache_path, name)
    if not path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as file:
        if file_contents := file.read():
            return json.loads(file_contents)
    return None
