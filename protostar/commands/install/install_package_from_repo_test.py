# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest

from protostar.commands.install import installation_exceptions
from protostar.commands.install.install_package_from_repo import (
    install_package_from_repo,
)
from protostar.git.git import Git


@pytest.fixture
def repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_successful_installation(tmpdir: str, repo_url: str):

    repo = Git.init(Path(tmpdir))

    install_package_from_repo("foo", repo_url, Path(tmpdir), Path(tmpdir) / "lib")

    assert len(repo.get_submodules()) == 1


def test_not_initialized_repo(tmpdir: str, repo_url: str):
    with pytest.raises(installation_exceptions.InvalidLocalRepository):
        install_package_from_repo("foo", repo_url, Path(tmpdir), Path(tmpdir) / "lib")
