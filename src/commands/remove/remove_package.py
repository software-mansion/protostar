from git import InvalidGitRepositoryError
from git.repo import Repo

from src.commands.remove import removal_exceptions


def remove_package(package_name: str, repo_root_dir: str):
    try:
        repo = Repo(repo_root_dir)
        submodule = repo.submodule(package_name)
        submodule.remove(force=True)

    except InvalidGitRepositoryError as _err:
        raise removal_exceptions.InvalidLocalRepository()
    except (ValueError, IndexError, AttributeError) as _err:
        raise removal_exceptions.PackageNotFound()
