from os import getcwd, listdir, path
from typing import Callable

from attr import dataclass
from git.repo import Repo


@dataclass
class PackageInfo:
    name: str
    url: str


def pull_package_submodules(
    on_submodule_update_start: Callable[[PackageInfo], None]
) -> None:
    submodule_names = listdir(path.join(getcwd(), "lib"))
    repo = Repo(getcwd())

    for submodule in repo.submodules:
        if submodule.name in submodule_names:
            on_submodule_update_start(
                PackageInfo(name=submodule.name, url=submodule.url)
            )
            submodule.update(init=True)
