# pylint: disable=line-too-long
import os
from pathlib import Path

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
        self._process.expect("\\[uname:: -s]:")
        return self

    def expect_latest_release_response_prompt(self) -> Self:
        self._process.expect(
            f"\\[curl:: -L -s -H Accept: application/json {PROTOSTAR_REPO_URL}/releases/latest]:"
        )
        return self

    def expect_download_prompt(self, version: str, filename: str) -> Self:
        self._process.expect(
            f"\\[curl:: -L https://github.com/software-mansion/protostar/releases/download/v{version}/{filename}]:"
        )
        return self

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


def test_nothing(tmp_path: Path, github_response: str, latest_protostar_version: str):
    harness = run_testing_harness(home_path=tmp_path, shell="zsh")
    harness.expect_kernel_name_prompt()
    harness.send("Darwin")
    harness.expect("Retrieving the latest version")
    harness.expect_latest_release_response_prompt()
    harness.send(github_response)
    harness.expect_download_prompt(
        filename="protostar-macOS.tar.gz", version=latest_protostar_version
    )
    harness.expect(
        f"Downloading protostar from {PROTOSTAR_REPO_URL}/releases/download/v{latest_protostar_version}/protostar-macOS.tar.gz"
    )
