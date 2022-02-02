from os import path
from shutil import rmtree
from git.repo import Repo


def remove(
    package_name: str, path_to_repo_root: str, packages_directory: str = "./lib"
):
    # remove directory
    # path_to_package = path.join(packages_directory, package_name)
    # if path.exists(path_to_package):
    #     rmtree(path_to_package)

    # remove submodule
    submodule = Repo(path_to_repo_root).submodule(package_name)
    submodule.remove()
