from logging import getLogger
from os import getcwd, listdir, path
from typing import Any

from colorama import Fore
from git.repo import Repo

from src.commands.install.extract_info_from_repo_id import extract_info_from_repo_id
from src.commands.install.install_package_from_repo import install_package_from_repo


def handle_install_command(args: Any) -> None:
    if args.command != "install":
        return

    logger = getLogger()

    if args.package is not None and args.package != "":
        package_info = extract_info_from_repo_id(args.package)
        install_package_from_repo(
            package_info.name if args.name is None else args.name,
            package_info.url,
            repo_root_dir=getcwd(),
            destination="lib",
            tag=package_info.version,
        )
    else:
        submodule_names = listdir(path.join(getcwd(), "lib"))
        repo = Repo(getcwd())

        for submodule in repo.submodules:
            if submodule.name in submodule_names:
                logger.info(
                    "Installing %s%s%s %s(%s)%s",
                    Fore.CYAN,
                    submodule.name,
                    Fore.RESET,
                    Fore.LIGHTBLACK_EX,
                    submodule.url,
                    Fore.RESET,
                )
                submodule.update(init=True)
