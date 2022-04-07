from logging import getLogger
from os import path
from pathlib import Path
from typing import Optional

from git import InvalidGitRepositoryError
from git.objects import Submodule
from git.repo import Repo

from src.commands.install import installation_exceptions
from src.utils import log_color_provider


def install_package_from_repo(
    name: str,
    url: str,
    repo_root_dir: Path,
    destination: Path,
    tag: Optional[str] = None,
):
    logger = getLogger()

    try:
        repo = Repo(repo_root_dir)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository(
            """A git repository must be initialized in order to install packages.
- Did you run `protostar init`?
- Are you in the right directory?"""
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
