import pytest
from pytest import CaptureFixture

from protostar.scripting_runtime import ScriptRunner
from scripting.conftest import CreateScriptFixture


@pytest.fixture(name="script_runner")
def script_runner_fixture() -> ScriptRunner:
    return ScriptRunner()


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
