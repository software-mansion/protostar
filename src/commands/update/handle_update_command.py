from os import getcwd, listdir, path

from src.commands.update.update_package import update_package
from src.utils import retrieve_real_package_name


def handle_update_command(args) -> None:
    assert args.command == "update"

    # TODO: make root directories easier to maintain
    # https://github.com/software-mansion/protostar/issues/55
    root_repo_dir = getcwd()
    packages_dir = path.join(root_repo_dir, "lib")
    if args.package:
        package_name = retrieve_real_package_name(
            args.package, root_repo_dir, packages_dir
        )
        update_package(package_name, root_repo_dir, packages_dir)
    else:
        for package_name in listdir(packages_dir):
            update_package(package_name, root_repo_dir, packages_dir)
