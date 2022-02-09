from os import getcwd
from typing import Any

from src.commands.install.extract_info_from_repo_id import extract_info_from_repo_id
from src.commands.install.install_package_from_repo import install_package_from_repo


def handle_install_command(args: Any) -> None:
    if args.command != "install":
        return

    package_info = extract_info_from_repo_id(args.package)
    install_package_from_repo(
        package_info.name,
        package_info.url,
        package_info.version,
        repo_root_dir=getcwd(),
        destination="./lib",
    )
