# pylint: disable=too-many-arguments
import os
from pathlib import Path

import pytest

from .conftest import (
    GitHubResponse,
    ScriptTestingHarness,
    SimulateUnwrappingFixture,
    assert_config_file_includes_path_entry,
)


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
