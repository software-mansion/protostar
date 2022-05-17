# pylint: disable=redefined-outer-name
from pathlib import Path

import pytest
from attr import dataclass
from git.objects import Submodule
from git.repo import Repo
from pytest_mock import MockerFixture

from protostar.commands.install import installation_exceptions
from protostar.commands.install.install_package_from_repo import (
    install_package_from_repo,
)


@dataclass
class SubmoduleMock:
    path = "-A"


@pytest.fixture
def repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_successful_installation(tmpdir: str, repo_url: str, mocker: MockerFixture):
    Repo.init(tmpdir)

    add_submodule = mocker.patch.object(
        Submodule,
        attribute="add",
        autospec=True,
    )
    add_submodule.return_value = SubmoduleMock()

    install_package_from_repo("foo", repo_url, Path(tmpdir), Path(tmpdir) / "lib")

    add_submodule.assert_called_once()


def test_not_initialized_repo(tmpdir: str, repo_url: str):
    with pytest.raises(installation_exceptions.InvalidLocalRepository):
        install_package_from_repo("foo", repo_url, Path(tmpdir), Path(tmpdir) / "lib")
