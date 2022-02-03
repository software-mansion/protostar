import os
from pathlib import Path
from typing import List


def collect_subdirectories(root_dir: str) -> List[str]:
    assert Path(root_dir).is_dir(), f"{root_dir} is supposed to be a directory!"
    return [x[0] for x in os.walk(root_dir)]
