from os import path
from typing import Optional

import pytest
from git.cmd import Git
from git.repo import Repo

from src.commands.update.update_package import update_package


@pytest.fixture(name="package_name")
def fixture_package_name() -> str:
    return "foobar"


@pytest.fixture(name="repo_dir")
def fixture_repo_root_dir(tmpdir) -> str:
    return tmpdir


@pytest.fixture(name="packages_dir")
def fixture_packages_dir(repo_dir) -> str:
    return path.join(repo_dir, "./lib")


@pytest.fixture(name="repo")
def fixture_repo(repo_dir):
    return Repo().init(repo_dir)


@pytest.fixture(name="current_tag")
def fixture_current_tag() -> Optional[str]:
    return None


@pytest.fixture(name="submodule")
def fixture_submodule(
    repo: Repo, package_name: str, packages_dir: str, current_tag: Optional[str]
):
    package_dir = path.join(packages_dir, package_name)
    submodule = repo.create_submodule(
        package_name,
        package_dir,
        "https://github.com/software-mansion/starknet.py",
        current_tag,
    )
    repo.git.add(submodule.path)
    repo.index.commit("add submodule")
    return submodule


@pytest.mark.usefixtures("submodule")
@pytest.mark.parametrize("current_tag", ["0.1.0-alpha"])
def test_updating_specific_package(package_name: str, repo_dir: str, packages_dir: str):
    cmd = Git(path.join(packages_dir, package_name))
    current_tag = cmd.execute(["git", "describe", "--tags"])
    assert current_tag == "0.1.0-alpha"

    update_package(package_name, repo_dir, packages_dir)

    new_tag = cmd.execute(["git", "describe", "--tags"])
    assert new_tag != "0.1.0-alpha"


# def test_updating_all_packages():
#     pass


# def test_updating_when_repo_not_initiated():
#     pass


# def test_updating_not_existing_package():
#     pass
