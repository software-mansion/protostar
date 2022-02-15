from logging import getLogger
from os import getcwd, path
from typing import Any

from colorama import Fore

from src.commands.remove.remove_package import remove_package
from src.utils import retrieve_real_package_name


def handle_remove_command(args: Any):
    logger = getLogger()
    assert args.command == "remove"

    repo_root_dir = getcwd()
    package_name = retrieve_real_package_name(
        args.package, getcwd(), path.join(repo_root_dir, "lib")
    )

    logger.info("Removing %s%s%s", Fore.RED, package_name, Fore.RESET)
    remove_package(package_name, repo_root_dir)
