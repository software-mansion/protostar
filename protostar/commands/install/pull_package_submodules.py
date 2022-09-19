from os import listdir
from pathlib import Path
from typing import Callable

from attr import dataclass
from protostar.git.git_repository import GitRepository


@dataclass
class PackageInfo:
    name: str
    url: str


def pull_package_submodules(
    on_submodule_update_start: Callable[[PackageInfo], None],
    repo_dir: Path,
    libs_dir: Path,
) -> None:
    submodule_names = listdir(libs_dir)
    repo = GitRepository(repo_dir)
    submodules = repo.get_submodules()

    for name in submodules:
        if name in submodule_names:
            url = submodules[name].url
            path = submodules[name].path

            on_submodule_update_start(PackageInfo(name=name, url=url))
            repo.update_submodule(path, init=True)
