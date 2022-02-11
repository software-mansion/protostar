from os import mkdir, path

import pytest
from git.repo import Repo

from src.commands.install.pull_package_submodules import pull_package_submodules

# - repo
#   - lib
#     - package_repo (s)
# - repo_clone
#   - ...
# - package_repo
#   - foo.txt


@pytest.fixture(name="repo_dir")
def fixture_repo_dir(tmpdir: str) -> str:
    return path.join(tmpdir, "repo")


@pytest.fixture(name="repo_clone_dir")
def fixture_repo_clone_dir(tmpdir: str) -> str:
    return path.join(tmpdir, "repo_clone")


@pytest.fixture(name="package_repo_dir")
def fixture_package_repo_dir(tmpdir: str) -> str:
    return path.join(tmpdir, "package_repo")


@pytest.fixture
def fixture_package_repo(package_repo_dir: str) -> Repo:
    repo = Repo.init(package_repo_dir)

    with open(path.join(package_repo_dir, "foo.txt"), "w", encoding="utf-8") as file:
        file.write("foo")

    return repo


@pytest.fixture
def fixture_repo(repo_dir: str) -> Repo:
    return Repo.init(repo_dir)


# ----------------------------------- TESTS ---------------------------------- #


def test_pulling_all_package_submodules() -> None:
    return
