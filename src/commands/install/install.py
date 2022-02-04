from logging import getLogger
from os import path

from colorama import Fore
from git import InvalidGitRepositoryError, NoSuchPathError
from git.objects import Submodule
from git.repo import Repo
from src.commands.install import installation_exceptions
from src.commands.install.utils import extract_info_from_repo_id


def install(
    repo_id: str,
    path_to_repo_root: str,
    destination="./lib",
):
    """
    A function which installs a package as git submodule.
    :param repo_id: Repo identifier which can be accepted in the following three forms:
        - name — e.g. `software-mansion/starknet.py@0.1.0-alpha`
        - url — e.g. `https://github.com/software-mansion/protostar`
        - ssh — e.g. `git@github.com:software-mansion/protostar.git`
    """
    logger = getLogger()

    try:
        repo = Repo(path_to_repo_root)
    except InvalidGitRepositoryError as _err:
        raise installation_exceptions.InvalidLocalRepository()
    except NoSuchPathError as _err:
        raise installation_exceptions.InvalidLocalRepository()

    package_info = extract_info_from_repo_id(repo_id)

    package_dir = path.join(destination, package_info.name)

    logger.info(
        "Installing %s%s%s in %s %s(%s)%s",
        Fore.CYAN,
        package_info.name,
        Fore.RESET,
        package_dir,
        Fore.LIGHTBLACK_EX,
        package_info.url,
        Fore.RESET,
    )

    Submodule.add(
        repo,
        package_info.name,
        package_dir,
        package_info.url,
        package_info.version,
        depth=1,
    )
