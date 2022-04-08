from os import listdir
from pathlib import Path

import pytest
from git.repo import Repo

from src.commands.remove import removal_exceptions
from src.commands.remove.remove_package import remove_package


@pytest.fixture(name="package_name")
def fixture_package_name():
    return "foobar"


@pytest.fixture(name="repo_dir")
def fixture_path_to_repo_root(tmpdir) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="packages_dir")
def fixture_packages_dir(repo_dir: Path):
    return repo_dir / "lib"


@pytest.fixture(name="repo")
def fixture_repo(repo_dir: Path):
    return Repo().init(repo_dir)


@pytest.fixture(name="submodule")
def fixture_submodule(repo: Repo, package_name: str, packages_dir: Path):
    submodule = repo.create_submodule(
        package_name,
        packages_dir / package_name,
        "https://github.com/software-mansion/protostar",
    )
    repo.git.add(submodule.path)
    repo.index.commit("add submodule")
    return submodule


@pytest.mark.usefixtures("submodule")
def test_removing(package_name: str, repo_dir: Path, packages_dir: str):
    assert package_name in listdir(packages_dir)

    remove_package(package_name, repo_dir)

    assert package_name not in listdir(packages_dir)


@pytest.mark.usefixtures("repo")
def test_removing_not_existing_package(package_name: str, repo_dir: Path):
    with pytest.raises(removal_exceptions.PackageNotFound):
        remove_package(package_name, repo_dir)


def test_removing_without_repo(package_name: str, repo_dir: Path):
    with pytest.raises(removal_exceptions.InvalidLocalRepository):
        remove_package(package_name, repo_dir)
