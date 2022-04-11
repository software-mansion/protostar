import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from starkware.starkware_utils.error_handling import StarkException


def collect_immediate_subdirectories(root_dir: Path) -> List[str]:
    assert root_dir.is_dir(), f"{root_dir} is supposed to be a directory!"
    (root, dirs, _) = next(os.walk(str(root_dir.resolve())))
    return [str(Path(root, directory).resolve()) for directory in dirs]


def simplify_stark_exception_error_message(ex: StarkException) -> Optional[str]:
    if not ex.message:
        return None

    ex.message.rfind("Error message:")
    # TODO: ...


@dataclass
class TestSubject:
    """
    A dataclass consisting of identification of a single test bundle, and target functions
    """

    test_path: Path
    test_functions: List[dict]
