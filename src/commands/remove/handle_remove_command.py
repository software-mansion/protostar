from logging import getLogger
from typing import Any

from src.commands.remove.remove_package import remove_package
from src.utils import Project, log_color_provider, retrieve_real_package_name


def handle_remove_command(args: Any, project: Project):
    logger = getLogger()
    assert args.command == "remove"

    package_name = retrieve_real_package_name(
        args.package,
        project.project_root,
        project.project_root / project.config.libs_path,
    )

    logger.info(
        "Removing %s%s%s",
        log_color_provider.get_color("RED"),
        package_name,
        log_color_provider.get_color("RESET"),
    )
    remove_package(package_name, project.project_root)
