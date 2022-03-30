import os.path
import shutil
from pathlib import Path
from typing import Optional


def find_protostar_binary_dir() -> Optional[Path]:
    protostar_dir: Optional[Path] = None
    protostar_path = shutil.which("protostar")
    if protostar_path:
        protostar_dir = Path(os.path.split(protostar_path)[0])

    return protostar_dir
