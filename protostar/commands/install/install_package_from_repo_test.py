# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest

from protostar.commands.install.install_package_from_repo import (
    install_package_from_repo,
)
from protostar.git import GitRepository


@pytest.fixture
def repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_successful_installation(tmpdir: str, repo_url: str):
    install_package_from_repo("foo", repo_url, Path(tmpdir), Path(tmpdir) / "lib")

    # This implicitly tests whether the install command actually creates a repo
    repo = GitRepository.from_existing(Path(tmpdir))

    assert len(repo.get_submodule_name_to_submodule()) == 1
