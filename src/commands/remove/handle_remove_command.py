from logging import getLogger
from os import getcwd, path
from typing import Any

from src.commands.remove.remove_package import remove_package
from src.utils import log_color_provider, retrieve_real_package_name


def handle_remove_command(args: Any):
    logger = getLogger()
    assert args.command == "remove"

    # TODO: make root directories easier to maintain
    # https://github.com/software-mansion/protostar/issues/55
    repo_root_dir = getcwd()
    package_name = retrieve_real_package_name(
        args.package, getcwd(), path.join(repo_root_dir, "lib")
    )

    logger.info(
        "Removing %s%s%s",
        log_color_provider.get_color("RED"),
        package_name,
        log_color_provider.get_color("RESET"),
    )
    remove_package(package_name, repo_root_dir)
