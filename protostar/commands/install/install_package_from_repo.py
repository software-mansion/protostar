from logging import getLogger
from pathlib import Path
from typing import Optional

from protostar.commands.install import installation_exceptions
from protostar.io import log_color_provider
from protostar.git import Git, InvalidGitRepositoryException


def install_package_from_repo(
    name: str,
    url: str,
    repo_dir: Path,
    destination: Path,
    tag: Optional[str] = None,
):
    logger = getLogger()

    try:
        repo = Git.load_existing_repo(repo_dir)
    except InvalidGitRepositoryException as ex:
        raise installation_exceptions.InvalidLocalRepository(
            """A git repository must be initialized in order to install packages.
- Did you run `protostar init`?
- Are you in the right directory?"""
        ) from ex

    package_dir = destination / name

    logger.info(
        "Installing %s%s%s %s(%s)%s",
        log_color_provider.get_color("CYAN"),
        name,
        log_color_provider.get_color("RESET"),
        log_color_provider.get_color("GRAY"),
        url,
        log_color_provider.get_color("RESET"),
    )

    repo.add_submodule(url, package_dir, name, tag)
    repo.add(package_dir)
    repo.commit(f"add {name}")
