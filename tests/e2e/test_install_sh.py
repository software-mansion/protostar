from enum import Enum
from pathlib import Path

import pexpect
import pytest


class SupportedKernels(Enum):
    LINUX = "Linux"
    # TODO


class ScriptTestingHarness:
    def __init__(self, protostar_repo_root: Path) -> None:
        self._protostar_repo_root = protostar_repo_root

    def run(self, home_dir: Path) -> str:
        return pexpect.run(
            f'sh {str(self._protostar_repo_root / "install__testing_harness.sh")}'
        )


@pytest.fixture(name="script_testing_harness")
def script_testing_harness_fixture(protostar_repo_root: Path) -> ScriptTestingHarness:
    return ScriptTestingHarness(protostar_repo_root)


def test_nothing(script_testing_harness: ScriptTestingHarness, tmp_path: Path):
    output = script_testing_harness.run(home_dir=tmp_path)

    assert output is not None
