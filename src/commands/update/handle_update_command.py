from logging import getLogger
from os import getcwd, listdir, path

from src.commands.update.update_package import update_package
from src.commands.update.updating_exceptions import PackageAlreadyUpToDateException
from src.utils import retrieve_real_package_name


def handle_update_command(args) -> None:
    assert args.command == "update"

    # TODO: make root directories easier to maintain
    # https://github.com/software-mansion/protostar/issues/55
    root_repo_dir = getcwd()
    packages_dir = path.join(root_repo_dir, "lib")
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
