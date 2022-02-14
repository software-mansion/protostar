from os import mkdir, path

import pytest
from git.repo import Repo

from src.utils.load_normalized_to_real_name_map import load_normalized_to_real_name_map

# - repo_with_normal_name_package
#   - lib
#     - package (s)
# - repo_with_custom_name_package
#   - lib
#     - pkg (s)
# - package_repo
#   - foo.txt


@pytest.fixture
def package_normal_name():
    return "package"


@pytest.fixture
def package_custom_name():
    return "pkg"


@pytest.fixture
def packages_dir_name():
    return "lib"


@pytest.fixture
def repo_with_normal_name_package_dir(tmpdir):
    return path.join(tmpdir, "repo_a")


@pytest.fixture
def repo_with_custom_name_package_dir(tmpdir):
    return path.join(tmpdir, "repo_b")


@pytest.fixture
def package_repo_dir(tmpdir):
    return path.join(tmpdir, "package_repo")


@pytest.fixture
def package_repo(package_repo_dir: str):
    repo = Repo.init(package_repo_dir)

    with open(
        path.join(package_repo_dir, "foo.txt"), "w", encoding="utf-8"
    ) as some_file:
        some_file.write("foo")
        some_file.close()
    repo.git.add("-u")
    repo.index.commit("add foo.txt")

    return repo


@pytest.fixture
def repo_with_normal_name_package(
    package_repo,
    repo_with_normal_name_package_dir: str,
    package_normal_name: str,
    packages_dir_name: str,
    package_repo_dir: str,
):
    repo = Repo.init(repo_with_normal_name_package_dir)

    packages_dir = path.join(repo_with_normal_name_package_dir, packages_dir_name)
    mkdir(packages_dir)

    repo.create_submodule(
        package_normal_name,
        path.join(packages_dir, package_normal_name),
        package_repo_dir,
    )

    repo.git.add("-u")
    repo.index.commit("add package")


@pytest.fixture
def repo_with_custom_name_package(
    package_repo,
    repo_with_custom_name_package_dir: str,
    package_custom_name: str,
    packages_dir_name: str,
    package_repo_dir: str,
):
    repo = Repo.init(repo_with_custom_name_package_dir)

    packages_dir = path.join(repo_with_custom_name_package_dir, packages_dir_name)
    mkdir(packages_dir)

    repo.create_submodule(
        package_custom_name,
        path.join(packages_dir, package_custom_name),
        package_repo_dir,
    )

    repo.git.add("-u")
    repo.index.commit("add package")


def test_package_installed_under_normal_name(
    repo_with_normal_name_package_dir: str, packages_dir_name: str
):
    # bar()
    print(repo_with_normal_name_package_dir)
    load_normalized_to_real_name_map(
        repo_root_dir=repo_with_normal_name_package_dir,
        packages_dir=path.join(repo_with_normal_name_package_dir, packages_dir_name),
    )
