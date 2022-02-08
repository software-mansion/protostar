from os import path
from typing import Optional, cast

from git.cmd import Git
from git.exc import GitCommandError
from git.objects import Submodule
from git.repo import Repo


def update_package(package_name: str, repo_root_dir: str, packages_dir: str):
    repo = Repo(repo_root_dir)

    submodule = repo.submodule(package_name)

    cmd = Git(path.join(packages_dir, package_name))

    current_tag = Optional[str]
    try:
        current_tag = cmd.execute(["git", "describe", "--tags"])
    except GitCommandError as _err:
        current_tag = None

    cmd.execute(["git", "fetch", "--tags"])

    latest_tag = Optional[str]
    try:
        rev = cmd.execute(["git", "rev-list", "--tags", "--max-count=1"])
        latest_tag = cast(str, cmd.execute(["git", "describe", "--tags", rev]))
    except GitCommandError as _err:
        latest_tag = None

    if latest_tag != current_tag:
        package_url = submodule.url
        package_dir = submodule.path

        submodule.remove()
        Submodule.add(
            repo,
            package_name,
            package_dir,
            package_url,
            latest_tag,
            depth=1,
        )
