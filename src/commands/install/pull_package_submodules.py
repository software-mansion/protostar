from os import listdir
from pathlib import Path
from typing import Callable

from attr import dataclass
from git.repo import Repo


@dataclass
class PackageInfo:
    name: str
    url: str


def pull_package_submodules(
    on_submodule_update_start: Callable[[PackageInfo], None],
    repo_root_dir: Path,
    libs_dir: Path,
) -> None:
    submodule_names = listdir(libs_dir)
    repo = Repo(repo_root_dir)

    for submodule in repo.submodules:
        if submodule.name in submodule_names:
            on_submodule_update_start(
                PackageInfo(name=submodule.name, url=submodule.url)
            )
            repo.git.execute(["git", "submodule", "update", "--init", submodule.path])
