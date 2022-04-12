import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


def collect_immediate_subdirectories(root_dir: Path) -> List[str]:
    assert root_dir.is_dir(), f"{root_dir} is supposed to be a directory!"
    (root, dirs, _) = next(os.walk(str(root_dir.resolve())))
    return [str(Path(root, directory).resolve()) for directory in dirs]


def extract_core_info_from_stark_ex_message(msg: Optional[str]) -> Optional[str]:
    if not msg:
        return None

    prefix = "Error message: "
    start_index = msg.rfind(prefix)

    if start_index == -1:
        return None

    end_index = msg.find("\n", start_index)

    return msg[start_index + len(prefix) : end_index]


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """

    test_path: Path
    test_functions: List[dict]
