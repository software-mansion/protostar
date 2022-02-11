from os import getcwd, listdir, path

from src.commands.update.update_package import update_package


def handle_update_command(args) -> None:
    assert args.command == "update"

    if args.package:
        update_package(args.package, getcwd(), "lib")
    else:
        for package_name in listdir(path.join(getcwd(), "lib")):
            update_package(package_name, getcwd(), "lib")
