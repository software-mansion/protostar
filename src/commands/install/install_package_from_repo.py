from logging import getLogger
from os import path
from typing import Optional

from colorama import Fore
from git import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Submodule
from git.repo import Repo

from src.commands.install import installation_exceptions


def install_package_from_repo(
    name: str,
    url: str,
    tag: Optional[str],
    repo_root_dir: str,
    destination: str,
):
    logger = getLogger()

    try:
        repo = Repo(repo_root_dir)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository()
    except NoSuchPathError as _err:
        raise installation_exceptions.InvalidLocalRepository()

    package_dir = path.join(destination, name)

    logger.info(
        "Installing %s%s%s in %s %s(%s)%s",
        Fore.CYAN,
        name,
        Fore.RESET,
        package_dir,
        Fore.LIGHTBLACK_EX,
        url,
        Fore.RESET,
    )

    Submodule.add(
        repo,
        name,
        package_dir,
        url,
        tag,
        depth=1,
    )
