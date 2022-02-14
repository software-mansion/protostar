# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
from os import mkdir, path

import pytest
from git.repo import Repo
from pytest_mock import MockerFixture

from src.utils.create_and_commit_sample_file import create_and_commit_sample_file
from src.utils.load_normalized_to_real_name_map import load_normalized_to_real_name_map
from src.utils.package_info.extract_info_from_repo_id import PackageInfo

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

    create_and_commit_sample_file(repo, package_repo_dir)

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


@pytest.mark.usefixtures("repo_with_normal_name_package")
def test_package_installed_without_custom_name(
    repo_with_normal_name_package_dir: str,
    package_normal_name: str,
    packages_dir_name: str,
    mocker: MockerFixture,
):

    mocked_extract_info_from_repo_id = mocker.patch(
        "src.utils.load_normalized_to_real_name_map.extract_info_from_repo_id",
    )
    mocked_extract_info_from_repo_id.return_value = PackageInfo(
        name=package_normal_name, url="", version=None
    )

    mapping = load_normalized_to_real_name_map(
        repo_root_dir=repo_with_normal_name_package_dir,
        packages_dir=path.join(repo_with_normal_name_package_dir, packages_dir_name),
    )

    assert mapping[package_normal_name] == package_normal_name


@pytest.mark.usefixtures("repo_with_custom_name_package")
def test_package_installed_with_custom_name(
    repo_with_custom_name_package_dir: str,
    package_custom_name: str,
    package_normal_name: str,
    packages_dir_name: str,
    mocker: MockerFixture,
):

    mocked_extract_info_from_repo_id = mocker.patch(
        "src.utils.load_normalized_to_real_name_map.extract_info_from_repo_id",
    )
    mocked_extract_info_from_repo_id.return_value = PackageInfo(
        name=package_normal_name, url="", version=None
    )

    mapping = load_normalized_to_real_name_map(
        repo_root_dir=repo_with_custom_name_package_dir,
        packages_dir=path.join(repo_with_custom_name_package_dir, packages_dir_name),
    )

    assert mapping[package_normal_name] == package_custom_name
