from git import InvalidGitRepositoryError
from git.repo import Repo

from src.commands.remove import removal_exceptions
from pathlib import Path


def remove_package(package_name: str, repo_root_dir: Path):
    try:
        repo = Repo(repo_root_dir)
        submodule = repo.submodule(package_name)
        submodule.remove(force=True)

    except InvalidGitRepositoryError as _err:
        raise removal_exceptions.InvalidLocalRepository(
            """A git repository must be initialized in order to remove packages.
- Did you run `protostar init`?
- Are you in the right directory?"""
        )
    except (ValueError, IndexError, AttributeError) as _err:
        raise removal_exceptions.PackageNotFound(
            f"Protostar couldn't find the following package: {package_name}"
        )
