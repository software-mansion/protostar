from git import InvalidGitRepositoryError
from git.repo import Repo

from . import removal_exceptions


def remove(package_name: str, path_to_repo_root: str):
    try:
        submodule = Repo(path_to_repo_root).submodule(package_name)
        submodule.remove()
    except InvalidGitRepositoryError as _err:
        raise removal_exceptions.InvalidLocalRepository()
    except (ValueError, IndexError, AttributeError) as _err:
        raise removal_exceptions.PackageNotFound()
