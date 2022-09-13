from dataclasses import dataclass
from pathlib import Path
from shutil import copytree
from typing import Optional

import pexpect
import pytest
from typing_extensions import Protocol

PROTOSTAR_REPO_URL = "https://github.com/software-mansion/protostar"

INSTALL_TESTING_HARNESS_PATH = (
    Path(__file__).parent / "install_testing_harness.sh"
).resolve()


class SupportedKernel:
    DARWIN = "Darwin"
    LINUX = "Linux"


class SupportedHardwareName:
    ARM64 = "arm64"
    X86_64 = "x86_64"


class UploadedInstallationFilename:
    LINUX = "protostar-Linux.tar.gz"
    MACOS = "protostar-macOS.tar.gz"
    MACOS_ARM64 = "protostar-macOS-arm64.tar.gz"


@dataclass
class Shell:
    interpreter: str
    name: str
    config_file_path: Path


class SupportedShell:
    ZSH = Shell(interpreter="/bin/zsh", name="zsh", config_file_path=Path("./.zshrc"))
    BASH = Shell(
        interpreter="/bin/bash", name="bash", config_file_path=Path("./.bashrc")
    )


class ScriptTestingHarness:
    def __init__(self, process: pexpect.spawn) -> None:
        self._process = process

    @classmethod
    def create(
        cls, home_path: Path, shell_interpreter: str, requested_version: str = ""
    ) -> "ScriptTestingHarness":
        command = f"bash {INSTALL_TESTING_HARNESS_PATH} {home_path} {shell_interpreter} {requested_version}"
        process = pexpect.spawn(command, timeout=1)
        return cls(process)

    def expect(self, response: str) -> None:
        self._process.expect(response)

    def expect_kernel_name_uname_prompt(self) -> None:
        self.expect("\\[uname -s]:")

    def expect_hardware_name_uname_prompt(self) -> None:
        self.expect("\\[uname -m]:")

    def expect_release_response_curl_prompt(self, requested_ref: str) -> None:
        self.expect(
            f"\\[curl -L -s -H Accept: application/json {PROTOSTAR_REPO_URL}/releases/{requested_ref}]:"
        )

    def expect_download_curl_prompt(self, filename: str, version: str) -> None:
        self.expect(
            f"\\[curl -L {PROTOSTAR_REPO_URL}/releases/download/v{version}/{filename}]:"
        )

    def expect_tar_call(self, data: str) -> None:
        self.expect(f"\\[tar {data}]")

    def expect_detected_shell(self, shell_name: str) -> None:
        self.expect(f"Detected your preferred shell is {shell_name}")

    def expect_eof(self) -> None:
        self._process.expect(pexpect.EOF)

    def send(self, value: str) -> None:
        self._process.sendline(value)


class ProtostarGitHubRepository:
    @staticmethod
    def get_release_not_found_response() -> str:
        return '{"error":"Not Found"}'

    @staticmethod
    def get_release_ref(version: Optional[str]) -> str:
        if version is None:
            return "latest"
        return f"tag/v{version}"

    @staticmethod
    def get_release_found_response(version: str) -> str:
        return f'"tag_name":"v{version}"'


class CreateFakeProtostarFixture(Protocol):
    def __call__(self, output_dir: Path) -> None:
        ...


@pytest.fixture(name="create_fake_protostar")
def create_fake_protostar_fixture(
    datadir: Path,
) -> CreateFakeProtostarFixture:
    def create_fake_protostar(output_dir: Path):
        copytree(src=datadir / "dist", dst=output_dir / ".protostar" / "dist")

    return create_fake_protostar


def assert_config_file_includes_path_entry(file_path: Path, home_path: Path):
    assert file_path.exists()
    protostar_path_entry = (
        f'export PATH="$PATH:{home_path.resolve()}/.protostar/dist/protostar'
    )
    assert protostar_path_entry in file_path.read_text()
