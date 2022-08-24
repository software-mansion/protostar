# pylint: disable=too-many-arguments
import os
from pathlib import Path
from shutil import copytree

import pexpect
import pytest
from typing_extensions import Protocol

PROTOSTAR_REPO_URL = "https://github.com/software-mansion/protostar"


@pytest.fixture(autouse=True)
def setup(protostar_repo_root: Path):
    cwd = Path()
    os.chdir(protostar_repo_root)
    yield
    os.chdir(cwd)


@pytest.fixture(name="home_path")
def home_path_fixture(tmp_path: Path):
    return tmp_path


@pytest.fixture(name="latest_protostar_version")
def latest_protostar_version_fixture() -> str:
    return "9.9.9"


class SimulateUnwrappingFixture(Protocol):
    def __call__(self, output_dir: Path) -> None:
        ...


@pytest.fixture(name="simulate_unwrapping")
def simulate_unwrapping_fixture(datadir: Path) -> SimulateUnwrappingFixture:
    def simulate_unwrapping(output_dir: Path):
        copytree(src=datadir / "dist", dst=output_dir / ".protostar" / "dist")

    return simulate_unwrapping


@pytest.mark.parametrize(
    "kernel, tar_filename, shell, shell_name, shell_config_path",
    (
        ("Darwin", "protostar-macOS.tar.gz", "/bin/zsh", "zsh", Path("./.zshrc")),
        ("Linux", "protostar-Linux.tar.gz", "/bin/bash", "bash", Path("./.bashrc")),
    ),
)
def test_installing_latest_version(
    home_path: Path,
    latest_protostar_version: str,
    simulate_unwrapping: SimulateUnwrappingFixture,
    kernel: str,
    tar_filename: str,
    shell: str,
    shell_name: str,
    shell_config_path: Path,
):

    harness = ScriptTestingHarness.create(home_path=home_path, shell=shell)

    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)

    harness.expect_release_response_curl_prompt(requested_ref="latest")
    harness.send(GitHubResponse.get_release_found_response(latest_protostar_version))

    harness.expect_download_curl_prompt(tar_filename, latest_protostar_version)
    harness.send("DATA")

    harness.expect_tar_info(data="DATA")
    simulate_unwrapping(output_dir=home_path)

    harness.expect_detected_shell(shell_name=shell_name)

    assert_config_file_includes_path_entry(
        file_path=home_path / shell_config_path, home_path=home_path
    )


@pytest.mark.parametrize(
    "kernel, tar_filename, shell, shell_name, shell_config_path",
    (
        ("Darwin", "protostar-macOS.tar.gz", "/bin/zsh", "zsh", Path("./.zshrc")),
        ("Linux", "protostar-Linux.tar.gz", "/bin/bash", "bash", Path("./.bashrc")),
    ),
)
def test_installing_specific_version(
    home_path: Path,
    simulate_unwrapping: SimulateUnwrappingFixture,
    kernel: str,
    tar_filename: str,
    shell: str,
    shell_name: str,
    shell_config_path: Path,
):
    requested_version = "0.1.0"

    harness = ScriptTestingHarness.create(
        home_path=home_path, shell=shell, requested_version=requested_version
    )

    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)

    harness.expect_release_response_curl_prompt(
        requested_ref=f"tag/v{requested_version}"
    )
    harness.send(GitHubResponse.get_release_found_response(requested_version))

    harness.expect_download_curl_prompt(tar_filename, requested_version)
    harness.send("DATA")

    harness.expect_tar_info(data="DATA")
    simulate_unwrapping(output_dir=home_path)

    harness.expect_detected_shell(shell_name=shell_name)

    assert_config_file_includes_path_entry(
        file_path=home_path / shell_config_path, home_path=home_path
    )


@pytest.mark.parametrize(
    "kernel, shell",
    (
        ("Darwin", "/bin/zsh"),
        ("Linux", "/bin/bash"),
    ),
)
def test_installing_specific_but_unreleased_version(
    home_path: Path,
    kernel: str,
    shell: str,
):
    unreleased_version = "99.9.9"
    harness = ScriptTestingHarness.create(
        home_path=home_path, shell=shell, requested_version=unreleased_version
    )

    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)

    harness.expect_release_response_curl_prompt(
        requested_ref=f"tag/v{unreleased_version}"
    )
    harness.send(GitHubResponse.get_release_not_found_response())

    harness.expect(f"Version {unreleased_version} not found")


def assert_config_file_includes_path_entry(file_path: Path, home_path: Path):
    assert file_path.exists()
    protostar_path_entry = (
        f'export PATH="$PATH:{home_path.resolve()}/.protostar/dist/protostar'
    )
    with open(file_path, encoding="utf-8") as file_handle:
        file_content = file_handle.read()
        assert protostar_path_entry in file_content


class GitHubResponse:
    @staticmethod
    def get_release_not_found_response():
        return '{"error":"Not Found"}'

    @staticmethod
    def get_release_found_response(version: str):
        return f'"tag_name":"v{version}"'


class ScriptTestingHarness:
    def __init__(self, process: pexpect.spawn) -> None:
        self._process = process

    @classmethod
    def create(
        cls, home_path: Path, shell: str, requested_version: str = ""
    ) -> "ScriptTestingHarness":
        command = (
            f"bash ./install_testing_harness.sh {home_path} {shell} {requested_version}"
        )
        process = pexpect.spawn(command, timeout=1)
        return cls(process)

    def expect(self, response: str) -> None:
        self._process.expect(response)

    def expect_kernel_name_uname_prompt(self) -> None:
        self.expect("\\[uname -s]:")

    def expect_release_response_curl_prompt(self, requested_ref: str) -> None:
        self.expect(
            f"\\[curl -L -s -H Accept: application/json {PROTOSTAR_REPO_URL}/releases/{requested_ref}]:"
        )

    def expect_download_curl_prompt(self, filename: str, version: str) -> None:
        self.expect(
            f"\\[curl -L {PROTOSTAR_REPO_URL}/releases/download/v{version}/{filename}]:"
        )

    def expect_tar_info(self, data: str) -> None:
        self.expect(f"\\[tar {data}]")

    def expect_detected_shell(self, shell_name: str) -> None:
        self.expect(f"Detected your preferred shell is {shell_name}")

    def send(self, value: str) -> None:
        self._process.sendline(value)
