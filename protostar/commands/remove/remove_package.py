from pathlib import Path
from typing import cast

from protostar.git import GitRepository, InvalidGitRepositoryException
from protostar.commands.remove import removal_exceptions


def remove_package(package_name: str, repo_dir: Path):
    try:
        repo = GitRepository.from_existing(repo_dir)
    except InvalidGitRepositoryException as ex:
        raise removal_exceptions.InvalidLocalRepository(
            """A git repository must be initialized in order to remove packages.
- Have you installed any packages?
- Are you in the right directory?"""
        ) from ex

    submodules = repo.get_name_to_submodule()

    if package_name not in submodules:
        raise removal_exceptions.PackageNotFound(
            f"Protostar couldn't find the following package: {package_name}"
        )

    repo.remove_submodule(cast(Path, submodules[package_name].path))
    repo.commit(f"remove {package_name}")
