from logging import getLogger
from pathlib import Path
from typing import Any, Optional, cast

from protostar.commands.update.updating_exceptions import (
    PackageAlreadyUpToDateException,
)
from protostar.git import GitRepository, ProtostarGitException
from protostar.io import log_color_provider


def update_package(package_name: str, repo_dir: Path, packages_dir: Path):
    logger = getLogger()

    repo = GitRepository.from_existing(repo_dir)

    submodules = repo.get_submodule_name_to_submodule()
    submodule = submodules[package_name]

    package_repo = GitRepository.from_existing(packages_dir / package_name)

    current_tag = Optional[str]
    try:
        current_tag = package_repo.get_tag()
    except ProtostarGitException:
        current_tag = None

    package_repo.fetch_tags()

    latest_tag: Any
    try:
        rev = package_repo.get_tag_rev()
        latest_tag = package_repo.get_tag(rev)
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
                tag=latest_tag,
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
        logger.warning(
            "Fetching from the mainline. The mainline can be in the non-releasable state.",
        )

        repo.update_submodule(package_dir)
