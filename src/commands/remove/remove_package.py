from git import InvalidGitRepositoryError
from git.repo import Repo

from src.commands.remove import removal_exceptions


def remove_package(package_name: str, repo_root_dir: str):
    try:
        repo = Repo(repo_root_dir)
        submodule = repo.submodule(package_name)
        submodule.remove(force=True)

    except InvalidGitRepositoryError as _err:
        raise removal_exceptions.InvalidLocalRepository(
            """Git repository must be initialized in order to remove packages.
Run `protostar init` or `git init` to create a git repository."""
        )
    except (ValueError, IndexError, AttributeError) as _err:
        raise removal_exceptions.PackageNotFound(
            f"Protostar couldn't find the following package: {package_name}"
        )
