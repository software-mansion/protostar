from logging import getLogger
from os import path

from colorama import Fore
from git import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Submodule
from git.repo import Repo

from src.commands.install import installation_exceptions
from src.commands.install.utils import map_url_or_ssh_to_package_name


def install(
    url_or_ssh: str,
    path_to_repo_root: str,
    destination="./lib",
):
    logger = getLogger()

    try:
        repo = Repo(path_to_repo_root)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository()
    except NoSuchPathError as _err:
        raise installation_exceptions.InvalidLocalRepository()

    package_name = map_url_or_ssh_to_package_name(url_or_ssh)
    package_dir = path.join(destination, package_name)

    logger.info(
        "Installing %s%s%s in %s %s(%s)%s",
        Fore.CYAN,
        package_name,
        Fore.RESET,
        package_dir,
        Fore.LIGHTBLACK_EX,
        url_or_ssh,
        Fore.RESET,
    )

    Submodule.add(
        repo,
        package_name,
        package_dir,
        url_or_ssh,
    )
