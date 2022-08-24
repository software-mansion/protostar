from pathlib import Path
from shutil import copytree

import pexpect
import pytest
from typing_extensions import Protocol

PROTOSTAR_REPO_URL = "https://github.com/software-mansion/protostar"

INSTALL_TESTING_HARNESS_PATH = (
    Path(__file__).parent / "install_testing_harness.sh"
).resolve()


class ScriptTestingHarness:
    def __init__(self, process: pexpect.spawn) -> None:
        self._process = process

    @classmethod
    def create(
        cls, home_path: Path, shell: str, requested_version: str = ""
    ) -> "ScriptTestingHarness":
        command = f"bash {INSTALL_TESTING_HARNESS_PATH} {home_path} {shell} {requested_version}"
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


class GitHubResponse:
    @staticmethod
    def get_release_not_found_response():
        return '{"error":"Not Found"}'

    @staticmethod
    def get_release_found_response(version: str):
        return f'"tag_name":"v{version}"'


class SimulateUnwrappingFixture(Protocol):
    def __call__(self, output_dir: Path) -> None:
        ...


@pytest.fixture(name="simulate_unwrapping")
def simulate_unwrapping_fixture(datadir: Path) -> SimulateUnwrappingFixture:
    def simulate_unwrapping(output_dir: Path):
        copytree(src=datadir / "dist", dst=output_dir / ".protostar" / "dist")

    return simulate_unwrapping


def assert_config_file_includes_path_entry(file_path: Path, home_path: Path):
    assert file_path.exists()
    protostar_path_entry = (
        f'export PATH="$PATH:{home_path.resolve()}/.protostar/dist/protostar'
    )
    with open(file_path, encoding="utf-8") as file_handle:
        file_content = file_handle.read()
        assert protostar_path_entry in file_content
