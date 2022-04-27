from logging import getLogger
from typing import Any

from src.commands.install.install_package_from_repo import install_package_from_repo
from src.commands.install.pull_package_submodules import pull_package_submodules
from src.utils import Project, extract_info_from_repo_id, log_color_provider


def handle_install_command(args: Any, project: Project) -> None:
    assert args.command == "install"

    logger = getLogger()

    repo_root_dir = project.project_root
    libs_dir = project.project_root / project.config.libs_path

    if args.package is not None and args.package != "":
        package_info = extract_info_from_repo_id(args.package)

        install_package_from_repo(
            package_info.name if args.name is None else args.name,
            package_info.url,
            repo_root_dir=project.project_root,
            destination=project.project_root / project.config.libs_path,
            tag=package_info.version,
        )
    else:
        pull_package_submodules(
            on_submodule_update_start=lambda package_info: logger.info(
                "Installing %s%s%s %s(%s)%s",
                log_color_provider.get_color("CYAN"),
                package_info.name,
                log_color_provider.get_color("RESET"),
                log_color_provider.get_color("GRAY"),
                package_info.url,
                log_color_provider.get_color("RESET"),
            ),
            repo_root_dir=repo_root_dir,
            libs_dir=libs_dir,
        )
