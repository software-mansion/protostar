from os import path

import pytest
from git.repo import Repo

from src.commands.remove import remove


@pytest.fixture(name="package_name")
def fixture_package_name():
    return "foobar"


@pytest.fixture(name="path_to_repo_root")
def fixture_root_repo_dir(tmpdir):
    return tmpdir


@pytest.fixture(name="packages_directory")
def fixture_packages_directory(path_to_repo_root):
    return path.join(path_to_repo_root, "./lib")


@pytest.fixture(name="repo")
def fixture_repo(path_to_repo_root):
    return Repo().init(path_to_repo_root)


@pytest.fixture(name="submodule")
def fixture_submodule(repo: Repo, package_name: str, packages_directory: str):
    path_to_package = path.join(packages_directory, package_name)
    submodule = repo.create_submodule(
        package_name,
        path_to_package,
        "https://github.com/software-mansion/protostar",
    )
    repo.git.add(submodule.path)
    repo.index.commit("add submodule")
    return submodule


@pytest.mark.usefixtures("submodule")
def test_base_case(package_name: str, path_to_repo_root: str, packages_directory: str):
    remove(package_name, path_to_repo_root, packages_directory)
