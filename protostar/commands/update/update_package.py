from logging import getLogger
from pathlib import Path
from typing import Any, Optional, cast


from protostar.commands.update.updating_exceptions import (
    PackageAlreadyUpToDateException,
)
from protostar.utils import log_color_provider

from protostar.git import Git, ProtostarGitException


def update_package(package_name: str, repo_dir: Path, packages_dir: Path):
    logger = getLogger()

    repo = Git.load_existing_repo(repo_dir)

    submodules = repo.get_submodules()
    submodule = submodules[package_name]

    package_repo = Git.load_existing_repo(packages_dir / package_name)

    current_tag = Optional[str]
    try:
        current_tag = package_repo.get_current_tag()
    except ProtostarGitException:
        current_tag = None

    package_repo.fetch_tags()

    latest_tag: Any
    try:
        latest_tag = package_repo.get_current_tag()
    except ProtostarGitException:
        latest_tag = None

    package_url = submodule.url
    package_dir = cast(Path, submodule.path)

    if current_tag is not None:
        if latest_tag != current_tag:

            repo.remove_submodule(package_dir)
            repo.add_submodule(
                url=package_url,
                submodule_path=package_dir,
                name=package_name,
                branch=latest_tag,
            )

            logger.info(
                "Updating %s%s%s (%s -> %s)",
                log_color_provider.get_color("CYAN"),
                package_name,
                log_color_provider.get_color("RESET"),
                current_tag,
                latest_tag,
            )
        else:
            raise PackageAlreadyUpToDateException()
    else:
        logger.info(
            "Updating %s%s%s",
            log_color_provider.get_color("CYAN"),
            package_name,
            log_color_provider.get_color("RESET"),
        )

        repo.update_submodule(package_dir)
