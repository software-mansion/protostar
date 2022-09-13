from pathlib import Path

import pytest

from tests.e2e.installation_script.conftest import (
    CreateFakeProtostarFixture,
    ProtostarGitHubRepository,
    ScriptTestingHarness,
    Shell,
    SupportedHardwareName,
    SupportedKernel,
    SupportedShell,
    UploadedInstallationFilename,
    assert_config_file_includes_path_entry,
)


@pytest.fixture(name="home_path")
def home_path_fixture(tmp_path: Path):
    return tmp_path


@pytest.fixture(name="latest_protostar_version")
def latest_protostar_version_fixture() -> str:
    return "9.9.9"


@pytest.mark.parametrize(
    "kernel, shell, hardware_name, uploaded_installation_filename",
    (
        (
            SupportedKernel.DARWIN,
            SupportedShell.ZSH,
            SupportedHardwareName.X86_64,
            UploadedInstallationFilename.MACOS,
        ),
        (
            SupportedKernel.DARWIN,
            SupportedShell.ZSH,
            SupportedHardwareName.X86_64,
            UploadedInstallationFilename.MACOS_ARM64,
        ),
        (
            SupportedKernel.LINUX,
            SupportedShell.BASH,
            "?",
            UploadedInstallationFilename.LINUX,
        ),
    ),
)
def test_installing_latest_version(
    home_path: Path,
    latest_protostar_version: str,
    create_fake_protostar: CreateFakeProtostarFixture,
    kernel: str,
    shell: Shell,
    hardware_name: str,
    uploaded_installation_filename: str,
):
    harness = ScriptTestingHarness.create(
        home_path=home_path, shell_interpreter=shell.interpreter
    )

    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)

    harness.expect_release_response_curl_prompt(
        requested_ref=ProtostarGitHubRepository.get_release_ref(version=None)
    )
    harness.send(
        ProtostarGitHubRepository.get_release_found_response(latest_protostar_version)
    )

    harness.expect_download_curl_prompt(
        uploaded_installation_filename, latest_protostar_version
    )
    create_fake_protostar(output_dir=home_path)
    harness.send("DATA")

    harness.expect_tar_call(data="DATA")

    harness.expect_detected_shell(shell_name=shell.name)
    harness.expect_eof()

    assert_config_file_includes_path_entry(
        file_path=home_path / shell.config_file_path, home_path=home_path
    )


@pytest.mark.parametrize(
    "kernel, shell, uploaded_installation_filename",
    (
        (
            SupportedKernel.DARWIN,
            SupportedShell.ZSH,
            UploadedInstallationFilename.MACOS,
        ),
        (
            SupportedKernel.LINUX,
            SupportedShell.BASH,
            UploadedInstallationFilename.LINUX,
        ),
    ),
)
def test_installing_specific_version(
    home_path: Path,
    create_fake_protostar: CreateFakeProtostarFixture,
    kernel: str,
    shell: Shell,
    uploaded_installation_filename: str,
):
    requested_version = "0.1.0"

    harness = ScriptTestingHarness.create(
        home_path=home_path,
        shell_interpreter=shell.interpreter,
        requested_version=requested_version,
    )

    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)

    harness.expect_release_response_curl_prompt(
        requested_ref=ProtostarGitHubRepository.get_release_ref(requested_version)
    )
    harness.send(
        ProtostarGitHubRepository.get_release_found_response(requested_version)
    )

    harness.expect_download_curl_prompt(
        uploaded_installation_filename, requested_version
    )
    create_fake_protostar(output_dir=home_path)
    harness.send("DATA")

    harness.expect_tar_call(data="DATA")

    harness.expect_detected_shell(shell_name=shell.name)
    harness.expect_eof()

    assert_config_file_includes_path_entry(
        file_path=home_path / shell.config_file_path, home_path=home_path
    )


@pytest.mark.parametrize(
    "kernel, shell",
    (
        (SupportedKernel.DARWIN, SupportedShell.ZSH),
        (SupportedKernel.LINUX, SupportedShell.BASH),
    ),
)
def test_installing_specific_but_unreleased_version(
    home_path: Path,
    kernel: str,
    shell: Shell,
):
    unreleased_version = "99.9.9"
    harness = ScriptTestingHarness.create(
        home_path=home_path,
        shell_interpreter=shell.interpreter,
        requested_version=unreleased_version,
    )

    harness.expect_kernel_name_uname_prompt()
    harness.send(kernel)

    harness.expect_release_response_curl_prompt(
        requested_ref=ProtostarGitHubRepository.get_release_ref(unreleased_version)
    )
    harness.send(ProtostarGitHubRepository.get_release_not_found_response())

    harness.expect(f"Version {unreleased_version} not found")
    harness.expect_eof()
