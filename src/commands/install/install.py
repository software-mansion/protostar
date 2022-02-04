from logging import getLogger
from os import path

from colorama import Fore
from git import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Submodule
from git.repo import Repo

from . import installation_exceptions
from .utils import map_url_or_ssh_to_package_name


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

    # pylint: disable=logging-fstring-interpolation
    logger.info(
        f"Installing {Fore.CYAN}%s{Fore.RESET} in %s {Fore.LIGHTBLACK_EX}(%s){Fore.RESET}",
        package_name,
        package_dir,
        url_or_ssh,
    )

    Submodule.add(
        repo,
        package_name,
        package_dir,
        url_or_ssh,
    )
