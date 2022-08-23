# pylint: disable=line-too-long
# pylint: disable=too-many-arguments
import os
from pathlib import Path
from shutil import copytree

import pexpect
import pytest

PROTOSTAR_REPO_URL = "https://github.com/software-mansion/protostar"


class ScriptTestingHarness:
    def __init__(self, process: pexpect.spawn) -> None:
        self._process = process

    def expect(self, response: str) -> None:
        self._process.expect(response)

    def expect_kernel_name_uname_prompt(self) -> None:
        self.expect("\\[uname -s]:")

    def expect_latest_release_response_curl_prompt(self) -> None:
        self.expect(
            f"\\[curl -L -s -H Accept: application/json {PROTOSTAR_REPO_URL}/releases/latest]:"
        )

    def expect_download_curl_prompt(self, filename: str, version: str) -> None:
        self.expect(
            f"\\[curl -L https://github.com/software-mansion/protostar/releases/download/v{version}/{filename}]:"
        )

    def expect_tar_info(self, data: str) -> None:
        self.expect(f"\\[tar {data}]")

    def expect_detected_shell(self, shell_name: str) -> None:
        self.expect(f"Detected your preferred shell is {shell_name}")

    def send(self, value: str) -> None:
        self._process.sendline(value)


def run_testing_harness(home_path: Path, shell: str) -> ScriptTestingHarness:
    command = f"sh ./install__testing_harness.sh {home_path} {shell}"
    process = pexpect.spawn(command, timeout=1)
    return ScriptTestingHarness(process)


@pytest.fixture(name="latest_protostar_version")
def latest_protostar_version_fixture() -> str:
    return "9.9.9"


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


@pytest.mark.parametrize(
    "kernel, tar_filename, shell, shell_name, shell_config_path",
    (
        ("Darwin", "protostar-macOS.tar.gz", "/bin/zsh", "zsh", Path("./.zshrc")),
        ("Linux", "protostar-Linux.tar.gz", "/bin/bash", "bash", Path("./.bashrc")),
    ),
)
def test_installing_latest_version(
    tmp_path: Path,
    latest_protostar_version: str,
    datadir: Path,
    kernel: str,
    tar_filename: str,
    shell: str,
    shell_name: str,
    shell_config_path: Path,
):
    fake_home_path = tmp_path

    harness = run_testing_harness(home_path=fake_home_path, shell=shell)
    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)
    harness.expect_latest_release_response_curl_prompt()
    harness.send(f'"tag_name":"v{latest_protostar_version}"')
    harness.expect_download_curl_prompt(tar_filename, latest_protostar_version)
    harness.send("DATA")
    harness.expect_tar_info(data="DATA")
    copytree(src=datadir / "dist", dst=fake_home_path / ".protostar" / "dist")
    harness.expect_detected_shell(shell_name=shell_name)

    assert_config_file_includes_path_entry(
        file_path=fake_home_path / shell_config_path, home_path=fake_home_path
    )


def assert_config_file_includes_path_entry(file_path: Path, home_path: Path):
    assert file_path.exists()
    protostar_path_entry = (
        f'export PATH="$PATH:{home_path.resolve()}/.protostar/dist/protostar'
    )
    with open(file_path, encoding="utf-8") as file_handle:
        file_content = file_handle.read()
        assert protostar_path_entry in file_content
