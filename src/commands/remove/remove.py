from git.repo import Repo


def remove(package_name: str, path_to_repo_root: str):
    submodule = Repo(path_to_repo_root).submodule(package_name)
    submodule.remove()
