# pylint: disable=line-too-long
import os
from pathlib import Path
from shutil import copytree

import pexpect
import pytest
from typing_extensions import Self

PROTOSTAR_REPO_URL = "https://github.com/software-mansion/protostar"


class TestingHarnessAPI:
    def __init__(self, process: pexpect.spawn) -> None:
        self._process = process

    def expect(self, response: str) -> Self:
        self._process.expect(response)
        return self

    def expect_kernel_name_prompt(self) -> Self:
        self._process.expect("\\[uname -s]:")
        return self

    def expect_latest_release_response_prompt(self) -> Self:
        self._process.expect(
            f"\\[curl -L -s -H Accept: application/json {PROTOSTAR_REPO_URL}/releases/latest]:"
        )
        return self

    def expect_download_prompt(self, version: str, filename: str) -> Self:
        self._process.expect(
            f"\\[curl -L https://github.com/software-mansion/protostar/releases/download/v{version}/{filename}]:"
        )
        return self

    def expect_tar(self, data: str):
        self._process.expect(f"\\[tar {data}]")

    def send(self, value: str) -> Self:
        self._process.sendline(value)
        return self


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
    harness.expect("Retrieving the latest version")
    harness.expect_latest_release_response_prompt()
    harness.send(github_response)
    harness.expect(
        f"Downloading protostar from {PROTOSTAR_REPO_URL}/releases/download/v{latest_protostar_version}/protostar-macOS.tar.gz"
    )
    harness.expect_download_prompt(
        filename="protostar-macOS.tar.gz", version=latest_protostar_version
    )
    harness.send("DATA")
    harness.expect_tar(data="DATA")
    copytree(src=datadir / "dist", dst=fake_home_path / ".protostar" / "dist")

    harness.expect("Detected your preferred shell is zsh")

    shell_config_file = fake_home_path / ".zshrc"
    assert shell_config_file.exists()
    assert_file_includes_content(
        file_path=shell_config_file,
        content=f'export PATH="$PATH:{fake_home_path.resolve()}/.protostar/dist/protostar',
    )


def assert_file_includes_content(file_path: Path, content: str):
    with open(file_path, encoding="utf-8") as file_handle:
        file_content = file_handle.read()
        assert content in file_content
