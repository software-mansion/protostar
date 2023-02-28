# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest

from protostar.commands.cairo0.install.install_package_from_repo import (
    install_package_from_repo,
)
from protostar.git import GitRepository


@pytest.fixture
def repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_successful_installation(tmpdir: str, repo_url: str):
    install_package_from_repo(
        name="foo",
        url=repo_url,
        project_root_path=Path(tmpdir),
        destination=Path(tmpdir) / "lib",
    )

    # This implicitly tests whether the install command actually creates a repo
    repo = GitRepository.from_existing(Path(tmpdir))

    assert len(repo.get_submodules()) == 1


def test_not_failing_when_package_was_already_installed(tmp_path: Path, repo_url: str):
    install_package_from_repo(
        name="foo",
        url=repo_url,
        project_root_path=tmp_path,
        destination=tmp_path / "lib",
    )
    install_package_from_repo(
        name="foo",
        url=repo_url,
        project_root_path=tmp_path,
        destination=tmp_path / "lib",
    )

    assert len(GitRepository.from_existing(tmp_path).get_submodules()) == 1
