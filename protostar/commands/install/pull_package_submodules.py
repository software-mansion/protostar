from os import listdir
from pathlib import Path
from typing import Callable

from protostar.git.git import Git
from protostar.utils.package_info import PackageInfo


def pull_package_submodules(
    on_submodule_update_start: Callable[[PackageInfo], None],
    repo_dir: Path,
    libs_dir: Path,
) -> None:
    submodule_names = listdir(libs_dir)
    repo = Git.from_existing(repo_dir)
    submodules = repo.get_submodules()

    for name in submodules:
        if name in submodule_names:
            on_submodule_update_start(submodules[name])
            repo.update_submodule(submodules[name].path, init=True)
