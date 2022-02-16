from logging import getLogger
from os import path
from typing import Optional

from git import InvalidGitRepositoryError
from git.objects import Submodule
from git.repo import Repo

from src.commands.install import installation_exceptions
from src.utils import log_color_provider


def install_package_from_repo(
    name: str,
    url: str,
    repo_root_dir: str,
    destination: str,
    tag: Optional[str] = None,
):
    logger = getLogger()

    try:
        repo = Repo(repo_root_dir)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository(
            "Git repository must be initialized in order to install packages because packages are installed as git submodules. Run `protostar init` or `git init` to create a git repository."
        )

    package_dir = path.join(destination, name)

    logger.info(
        "Installing %s%s%s %s(%s)%s",
        log_color_provider.get_color("CYAN"),
        name,
        log_color_provider.get_color("RESET"),
        log_color_provider.get_color("GRAY"),
        url,
        log_color_provider.get_color("RESET"),
    )

    submodule = Submodule.add(
        repo,
        name,
        package_dir,
        url,
        tag,
        depth=1,
    )

    repo.git.add(submodule.path)
    repo.index.commit(f"add {name}")
