from os import listdir
from pathlib import Path
from typing import Callable, cast

from protostar.git import GitRepository, InvalidGitRepositoryException
from protostar.package_manager import PackageInfo
from protostar.commands.install.installation_exceptions import InvalidLocalRepository


def pull_package_submodules(
    on_submodule_update_start: Callable[[PackageInfo], None],
    repo_dir: Path,
    libs_dir: Path,
) -> None:
    submodule_names = listdir(libs_dir)
    try:
        repo = GitRepository.create(repo_dir)
    except InvalidGitRepositoryException as ex:
        raise InvalidLocalRepository(
            "Git repository not found.\n"
            "Did you install any package before running this command?",
        ) from ex

    submodules = repo.get_submodules()

    for name in submodules:
        if name in submodule_names:
            on_submodule_update_start(submodules[name])
            repo.update_submodule(cast(Path, submodules[name].path))
