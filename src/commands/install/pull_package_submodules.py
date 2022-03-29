from os import listdir, path
from typing import Callable

from attr import dataclass
from git.repo import Repo


@dataclass
class PackageInfo:
    name: str
    url: str


def pull_package_submodules(
    on_submodule_update_start: Callable[[PackageInfo], None], repo_root_dir: str
) -> None:
    submodule_names = listdir(path.join(repo_root_dir, "lib"))
    repo = Repo(repo_root_dir)

    for submodule in repo.submodules:
        if submodule.name in submodule_names:
            on_submodule_update_start(
                PackageInfo(name=submodule.name, url=submodule.url)
            )
            repo.git.execute(["git", "submodule", "update", "--init", submodule.path])
