from os import listdir
from pathlib import Path
from py._path.local import LocalPath

import pytest

from protostar.commands.remove import removal_exceptions
from protostar.commands.remove.remove_package import remove_package
from protostar.git import Git, GitRepository


@pytest.fixture(name="package_name")
def fixture_package_name():
    return "foobar"


@pytest.fixture(name="repo_dir")
def fixture_path_to_repo_root(tmpdir: LocalPath) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="packages_dir")
def fixture_packages_dir(repo_dir: Path):
    return repo_dir / "lib"


@pytest.fixture(name="repo")
def fixture_repo(repo_dir: Path):
    return Git.init(repo_dir)


@pytest.fixture(name="submodule")
def fixture_submodule(repo: GitRepository, package_name: str, packages_dir: Path):

    path_to_package = packages_dir / package_name

    repo.add_submodule(
        url="https://github.com/software-mansion/protostar",
        submodule_path=path_to_package,
        name=package_name,
    )

    repo.add(path_to_package)
    repo.commit("add submodule")


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
