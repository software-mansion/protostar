from logging import getLogger
from os import listdir

from src.commands.update.update_package import update_package
from src.commands.update.updating_exceptions import PackageAlreadyUpToDateException
from src.utils import Project, retrieve_real_package_name


def handle_update_command(args, project: Project) -> None:
    assert args.command == "update"

    root_repo_dir = str(project.project_root)
    packages_dir = project.config.libs_path
    logger = getLogger()

    if args.package:
        package_name = retrieve_real_package_name(
            args.package, root_repo_dir, packages_dir
        )
        try:
            update_package(package_name, root_repo_dir, packages_dir)
        except PackageAlreadyUpToDateException as err:
            logger.info(err.message)
    else:
        for package_name in listdir(packages_dir):
            try:
                update_package(package_name, root_repo_dir, packages_dir)
            except PackageAlreadyUpToDateException:
                continue
