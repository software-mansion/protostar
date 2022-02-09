from os import path

import pytest
from git.repo import Repo

from src.commands.install import installation_exceptions
from src.commands.install.install_package_from_repo import install_package_from_repo


@pytest.fixture(name="repo_url")
def fixture_repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_successful_installation(tmpdir: str, repo_url: str):
    Repo.init(tmpdir)

    install_package_from_repo("foo", repo_url, None, tmpdir, path.join(tmpdir, "lib"))

    assert path.exists(path.join(tmpdir, "lib", "foo"))


def test_not_initialized_repo(tmpdir: str, repo_url: str):
    with pytest.raises(installation_exceptions.InvalidLocalRepository):
        install_package_from_repo(
            "foo", repo_url, None, tmpdir, path.join(tmpdir, "lib")
        )
