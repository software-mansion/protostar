from logging import getLogger
from pathlib import Path
from typing import Optional

from protostar.io import log_color_provider
from protostar.git import Git, InvalidGitRepositoryException


def install_package_from_repo(
    name: str,
    url: str,
    project_root_path: Path,
    destination: Path,
    tag: Optional[str] = None,
):
    logger = getLogger()

    try:
        repo = Git.load_existing_repo(project_root_path)
    except InvalidGitRepositoryException:
        logger.info("Initializing git repository.")
        repo = Git.init(project_root_path)

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
