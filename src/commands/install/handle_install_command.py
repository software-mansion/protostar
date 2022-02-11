from logging import getLogger
from os import getcwd
from typing import Any

from colorama import Fore

from src.commands.install.extract_info_from_repo_id import extract_info_from_repo_id
from src.commands.install.install_package_from_repo import install_package_from_repo
from src.commands.install.pull_package_submodules import pull_package_submodules


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
        pull_package_submodules(
            on_submodule_update_start=lambda package_info: logger.info(
                "Installing %s%s%s %s(%s)%s",
                Fore.CYAN,
                package_info.name,
                Fore.RESET,
                Fore.LIGHTBLACK_EX,
                package_info.url,
                Fore.RESET,
            )
        )
