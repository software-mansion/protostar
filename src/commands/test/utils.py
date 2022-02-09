import os
from dataclasses import dataclass
from pathlib import Path
from typing import List


def collect_subdirectories(root_dir: Path) -> List[str]:
    assert root_dir.is_dir(), f"{root_dir} is supposed to be a directory!"
    return [x[0] for x in os.walk(root_dir)]


def collect_immediate_subdirectories(root_dir: Path) -> List[str]:
    assert root_dir.is_dir(), f"{root_dir} is supposed to be a directory!"
    result = []
    (root, dirs, _) = next(os.walk(str(root_dir.resolve())))
    return [str(Path(root, directory).resolve()) for directory in dirs]
    return result


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """

    test_path: Path
    test_functions: List[dict]
