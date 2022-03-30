# pylint: disable=redefined-outer-name

from os import mkdir, path
from unittest.mock import MagicMock

import pytest
from git.repo import Repo
from pytest_mock import MockerFixture

from src.commands.install.pull_package_submodules import pull_package_submodules

# - repo
#   - lib
#     - package_repo (s)
# - repo_clone
#   - ...
# - package_repo
#   - foo.txt


@pytest.fixture
def packages_dir_name() -> str:
    return "lib"


@pytest.fixture
def the_packages_file_name() -> str:
    return "foo.txt"


@pytest.fixture
def the_package_name() -> str:
    return "package"


@pytest.fixture
def repo_dir(tmpdir: str) -> str:
    return path.join(tmpdir, "repo")


@pytest.fixture
def repo_clone_dir(tmpdir: str) -> str:
    return path.join(tmpdir, "repo_clone")


@pytest.fixture
def package_repo_dir(tmpdir: str) -> str:
    return path.join(tmpdir, "package_repo")


@pytest.fixture
def package_repo(package_repo_dir: str, the_packages_file_name: str) -> Repo:
    repo = Repo.init(package_repo_dir, initial_branch="main")

    the_file_path = path.join(package_repo_dir, the_packages_file_name)
    with open(path.join(the_file_path), "w", encoding="utf-8") as file:
        file.write("foo")

    repo.git.add("-A")
    repo.index.commit("add foo")

    assert path.exists(the_file_path)

    return repo


@pytest.fixture
# pylint: disable=unused-argument
def repo(
    repo_dir: str,
    package_repo_dir: str,
    packages_dir_name: str,
    the_package_name: str,
    package_repo: Repo,
) -> Repo:
    repo = Repo.init(repo_dir)

    packages_dir = path.join(repo_dir, packages_dir_name)
    package_dir = path.join(packages_dir, the_package_name)
    mkdir(packages_dir)
    repo.create_submodule(the_package_name, package_dir, package_repo_dir)

    repo.git.add()
    repo.index.commit("add submodule")

    return repo


@pytest.fixture
# pylint: disable=unused-argument
def repo_clone(
    repo_clone_dir: str, repo_dir: str, repo: Repo, packages_dir_name: str
) -> Repo:
    cloned_repo = repo.clone(repo_clone_dir)

    assert path.exists(
        path.join(repo_clone_dir, packages_dir_name)
    ), "./lib exists in the cloned repo directory"
    return cloned_repo


@pytest.mark.usefixtures("repo_dir", "repo_clone")
def test_pulling_all_package_submodules(
    repo_clone_dir: str,
    packages_dir_name: str,
    the_package_name: str,
    the_packages_file_name: str,
    mocker: MockerFixture,
) -> None:
    assert (
        path.exists(
            path.join(
                repo_clone_dir,
                packages_dir_name,
                the_package_name,
                the_packages_file_name,
            )
        )
        is False
    )
    callback: MagicMock = mocker.MagicMock()
    pull_package_submodules(
        on_submodule_update_start=callback, repo_root_dir=repo_clone_dir
    )

    callback.assert_called_once()
    assert path.exists(
        path.join(
            repo_clone_dir,
            packages_dir_name,
            the_package_name,
            the_packages_file_name,
        )
    )
