import pytest
from packaging.version import Version
from pytest import CaptureFixture
from pytest_mock import MockerFixture

from protostar.scripting_runtime import ScriptRunner
from protostar.self.protostar_directory import VersionManager
from scripting.conftest import CreateScriptFixture


@pytest.fixture(name="version_manager")
def version_manager_fixture(mocker: MockerFixture) -> VersionManager:
    version_manager = mocker.MagicMock()
    version_manager.protostar_version = Version("1.2.3")
    return version_manager


@pytest.fixture(name="script_runner")
def script_runner_fixture(version_manager: VersionManager) -> ScriptRunner:
    return ScriptRunner(
        version_manager=version_manager,
    )


def test_sys_info(
    create_script: CreateScriptFixture,
    script_runner: ScriptRunner,
    capfd: CaptureFixture[str],
):
    # language=python
    script = create_script(
        """
print(f"{__name__=}")
print(f"{__file__=}")
print(f"{__package__=}")

if __name__ == "__main__":
    print("__main__ pattern works!")
"""
    )

    script_runner.run(script)

    assert capfd.readouterr() == (
        f"""\
__name__='__main__'
__file__='{str(script)}'
__package__=''
__main__ pattern works!
""",
        "",
    )


def test_crash(
    create_script: CreateScriptFixture,
    script_runner: ScriptRunner,
    capfd: CaptureFixture[str],
):
    # language=python
    script = create_script(
        """
print("before crash")

lst = []
lst[1] = 0

print("after crash")
"""
    )

    script_runner.run(script)

    assert capfd.readouterr() == (
        "before crash\n",
        f"""\
Script {script}:
Traceback (most recent call last):
  File "{script}", line 5, in <module>
    lst[1] = 0
IndexError: list assignment index out of range
""",
    )


def test_protostar_scripting_version(
    version_manager: VersionManager,
    create_script: CreateScriptFixture,
    script_runner: ScriptRunner,
    capfd: CaptureFixture[str],
):
    # language=python
    script = create_script(
        """
import protostar.scripting

print(protostar.scripting.__version__)
"""
    )

    script_runner.run(script)

    assert capfd.readouterr() == (
        f"{str(version_manager.protostar_version)}\n",
        "",
    )
