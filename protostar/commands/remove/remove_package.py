from pathlib import Path

from git import InvalidGitRepositoryError
from git.repo import Repo


from protostar.git.git import Git

from protostar.commands.remove import removal_exceptions


def remove_package(package_name: str, repo_dir: Path):
    try:

        # repo = Git.from_existing(repo_dir)
        # repo.

        repo = Repo(repo_dir, search_parent_directories=True)
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
