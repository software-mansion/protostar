from os import path

import pytest
from git.objects import Submodule
from git.repo import Repo
from pytest_mock import MockerFixture

from src.commands.install import installation_exceptions
from src.commands.install.install_package_from_repo import install_package_from_repo


@pytest.fixture(name="repo_url")
def fixture_repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_successful_installation(tmpdir: str, repo_url: str, mocker: MockerFixture):
    Repo.init(tmpdir)

    add_submodule = mocker.patch.object(
        Submodule,
        attribute="add",
        autospec=True,
    )

    install_package_from_repo("foo", repo_url, tmpdir, path.join(tmpdir, "lib"))

    add_submodule.assert_called_once()


def test_not_initialized_repo(tmpdir: str, repo_url: str):
    with pytest.raises(installation_exceptions.InvalidLocalRepository):
        install_package_from_repo("foo", repo_url, tmpdir, path.join(tmpdir, "lib"))
