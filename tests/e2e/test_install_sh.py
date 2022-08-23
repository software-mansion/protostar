# pylint: disable=line-too-long
import os
from pathlib import Path
from shutil import copytree

import pexpect
import pytest

PROTOSTAR_REPO_URL = "https://github.com/software-mansion/protostar"


class TestingHarnessAPI:
    def __init__(self, process: pexpect.spawn) -> None:
        self._process = process

    def expect(self, response: str) -> None:
        self._process.expect(response)

    def expect_kernel_name_prompt(self) -> None:
        self.expect("\\[uname -s]:")

    def expect_latest_release_response_prompt(self) -> None:
        self.expect(
            f"\\[curl -L -s -H Accept: application/json {PROTOSTAR_REPO_URL}/releases/latest]:"
        )

    def expect_download_prompt(self, filename: str, version: str) -> None:
        self.expect(
            f"\\[curl -L https://github.com/software-mansion/protostar/releases/download/v{version}/{filename}]:"
        )

    def expect_tar_prompt(self, data: str) -> None:
        self.expect(f"\\[tar {data}]")

    def expect_detected_shell(self, shell_name: str) -> None:
        self.expect(f"Detected your preferred shell is {shell_name}")

    def send(self, value: str) -> None:
        self._process.sendline(value)


def run_testing_harness(home_path: Path, shell: str) -> TestingHarnessAPI:
    command = f"sh ./install__testing_harness.sh {home_path} {shell}"
    process = pexpect.spawn(command, timeout=1)
    return TestingHarnessAPI(process)


@pytest.fixture(name="latest_protostar_version")
def latest_protostar_version_fixture() -> str:
    return "0.3.2"


@pytest.fixture(name="github_response")
def github_response_fixture(latest_protostar_version: str):
    return f'"tag_name":"v{latest_protostar_version}"'


@pytest.fixture(autouse=True)
def setup(protostar_repo_root: Path):
    cwd = Path()
    os.chdir(protostar_repo_root)
    yield
    os.chdir(cwd)


@pytest.fixture(name="protostar_package")
def protostar_package_fixture(datadir: Path):
    with open(datadir / "protostar.tar.gz", mode="rb") as file_handle:
        return file_handle.read()


def test_installing_latest_version(
    tmp_path: Path, github_response: str, latest_protostar_version: str, datadir: Path
):
    fake_home_path = tmp_path

    harness = run_testing_harness(home_path=fake_home_path, shell="/bin/zsh")
    harness.expect_kernel_name_prompt()
    harness.send("Darwin")
    harness.expect_latest_release_response_prompt()
    harness.send(github_response)
    harness.expect_download_prompt("protostar-macOS.tar.gz", latest_protostar_version)
    harness.send("DATA")
    harness.expect_tar_prompt(data="DATA")
    copytree(src=datadir / "dist", dst=fake_home_path / ".protostar" / "dist")
    harness.expect_detected_shell(shell_name="zsh")

    protostar_path_entry = (
        f'export PATH="$PATH:{fake_home_path.resolve()}/.protostar/dist/protostar'
    )
    assert_file_includes_content(
        file_path=fake_home_path / ".zshrc", content=protostar_path_entry
    )


def assert_file_includes_content(file_path: Path, content: str):
    assert file_path.exists()
    with open(file_path, encoding="utf-8") as file_handle:
        file_content = file_handle.read()
        assert content in file_content
