from os import path

import pytest

from src.commands.update.update_package import update_package


@pytest.fixture(name="package_name")
def fixture_package_name() -> str:
    return "foobar"


@pytest.fixture(name="repo_root_dir")
def fixture_repo_root_dir(tmpdir) -> str:
    return tmpdir


@pytest.fixture(name="packages_dir")
def fixture_packages_dir(repo_root_dir) -> str:
    return path.join(repo_root_dir, "./lib")


def test_updating_specific_package(
    package_name: str, repo_root_dir: str, packages_dir: str
):
    update_package(package_name, repo_root_dir, packages_dir)


def test_updating_all_packages():
    pass


def test_updating_when_repo_not_initiated():
    pass


def test_updating_not_existing_package():
    pass
