from typing import cast

from git.cmd import Git
from git.objects import Submodule
from git.repo import Repo


def update_package(package_name: str, repo_root_dir: str, _packages_dir: str):
    repo = Repo(repo_root_dir)

    submodule = repo.submodule(package_name)

    print(submodule.path)

    cmd = Git(submodule.path)
    current_tag = cmd.execute(["git", "describe", "--tags"])
    cmd.execute(["git", "fetch", "--tags"])
    rev = cmd.execute(["git", "rev-list", "--tags", "--max-count=1"])
    latest_tag = cast(str, cmd.execute(["git", "describe", "--tags", rev]))

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
