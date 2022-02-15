# pylint: disable=redefined-outer-name
from os import mkdir, path

import pytest
from pytest_mock import MockerFixture

from src.utils.package_info import PackageInfo
from src.utils.retrieve_real_package_name import retrieve_real_package_name


@pytest.fixture
def repo_root_dir(tmpdir):
    repo_dir = path.join(tmpdir, "repo")
    mkdir(repo_dir)
    return repo_dir


@pytest.fixture
def packages_dir(repo_root_dir: str):
    packages_dir = path.join(repo_root_dir, "lib")
    mkdir(packages_dir)
    return packages_dir


@pytest.fixture
def package_name():
    return "package"


@pytest.fixture
def package_dir(packages_dir: str, package_name: str):
    package_dir = path.join(packages_dir, package_name)
    mkdir(package_dir)
    return package_dir


# @pytest.mark.parametrize("package_name", ["starknet_py"])
# @pytest.mark.usefixtures("package_dir")
# def test_name_supported_by_install_command(
#     repo_root_dir: str, packages_dir: str, package_name: str, mocker: MockerFixture
# ):

#     mocked_load_normalized_to_real_name_map = mocker.patch(
#         "src.utils.retrieve_real_package_name.load_normalized_to_real_name_map",
#     )
#     mocked_load_normalized_to_real_name_map.return_value = {
#         "starknet_py": "starknet_py",
#     }

#     result = retrieve_real_package_name(
#         "software-mansion/starknet.py", repo_root_dir, packages_dir
#     )
#     mocked_load_normalized_to_real_name_map.assert_called_once()
#     assert result == package_name


# def test_not_normalized_name(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name("starknet.py", repo_root_dir, packages_dir)


# def test_package_custom_name(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name("package_custom_name", repo_root_dir, packages_dir)


# def test_not_existing_package(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name("NOT_EXISTING_PACKAGE", repo_root_dir, packages_dir)
