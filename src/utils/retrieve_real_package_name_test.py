# pylint: disable=redefined-outer-name
from os import path

from src.utils.retrieve_real_package_name import retrieve_real_package_name


def repo_root_dir(tmpdir):
    return path.join(tmpdir, "repo")


def packages_dir(repo_root_dir: str):
    return path.join(repo_root_dir, "lib")


# def test_1(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name(
#         "software-mansion/starknet.py", repo_root_dir, packages_dir
#     )


# def test_2(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name("starknet.py", repo_root_dir, packages_dir)


# def test_3(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name("package_custom_name", repo_root_dir, packages_dir)


# def test_4(repo_root_dir: str, packages_dir: str):
#     retrieve_real_package_name("NOT_EXISTING_PACKAGE", repo_root_dir, packages_dir)
