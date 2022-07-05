# pylint: disable=broad-except
import os
import shutil
import tarfile
from logging import Logger
from pathlib import Path
from typing import Any

import requests

from protostar.utils.protostar_directory import (
    ProtostarDirectory,
    VersionManager,
    VersionType,
)

PROTOSTAR_REPO = "https://github.com/software-mansion/protostar"


class UpgradeManagerException(Exception):
    pass


class UpgradeManager:
    def __init__(
        self,
        protostar_directory: ProtostarDirectory,
        version_manager: VersionManager,
        logger: Logger,
    ):
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager
        self._logger = logger

    def upgrade(self):
        assert os.path.isdir(self._protostar_directory.directory_root_path)
        assert os.path.isdir(self._protostar_directory.directory_root_path / "dist")

        protostar_dir = self._protostar_directory.directory_root_path
        old_version = protostar_dir / "previous_version_tmp"

        platform = self.get_platform()
        tarball_name = f"protostar-{platform}.tar.gz"
        tarball_loc = protostar_dir / tarball_name

        current_version = (
            self._version_manager.protostar_version or VersionManager.parse("0.0.0")
        )
        latest_version_tag: str = self.get_latest_release()["tag_name"]

        latest_version = self._version_manager.parse(latest_version_tag)
        self._logger.info("Looking for a new version ...")
        if latest_version <= current_version:
            self._logger.info("Protostar is up to date")
            return

        self._logger.info(
            "Starting upgrade from version %s to version %s",
            current_version,
            latest_version,
        )
        try:
            self._pull_tarball(
                latest_version=latest_version,
                latest_version_tag=latest_version_tag,
                tarball_loc=tarball_loc,
                tarball_name=tarball_name,
            )
        except (Exception, SystemExit) as err:
            self._handle_error(
                err,
                current_version=current_version,
                old_version=old_version,
                protostar_dir=protostar_dir,
                tarball_loc=tarball_loc,
            )

        self._backup(protostar_dir, old_version)

        try:
            self._install_new_version(
                latest_version=latest_version,
                tarball_loc=tarball_loc,
                protostar_dir=protostar_dir,
            )
            self.cleanup(old_version=old_version, tarball_loc=tarball_loc)
        except KeyboardInterrupt:
            self._logger.info("Interrupting...")
            self._rollback(
                current_version=current_version,
                old_version=old_version,
                protostar_dir=protostar_dir,
            )
            self.cleanup(old_version=old_version, tarball_loc=tarball_loc)
        except (Exception, SystemExit) as err:
            self._handle_error(
                err,
                current_version=current_version,
                old_version=old_version,
                protostar_dir=protostar_dir,
                tarball_loc=tarball_loc,
            )

    def _handle_error(
        self,
        err: Any,
        current_version: VersionType,
        protostar_dir: Path,
        old_version: Path,
        tarball_loc: Path,
    ):
        self._logger.error(
            (
                "Upgrade failed\n"
                "You can run the following installation script instead:\n"
                "curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash"
            )
        )
        self._rollback(
            current_version, protostar_dir=protostar_dir, old_version=old_version
        )
        self.cleanup(old_version=old_version, tarball_loc=tarball_loc)
        raise err

    @staticmethod
    def _backup(protostar_dir: Path, old_version: Path):
        shutil.move(str(protostar_dir / "dist"), old_version)

    def _pull_tarball(
        self,
        latest_version: VersionType,
        latest_version_tag: str,
        tarball_name: str,
        tarball_loc: Path,
    ):
        self._logger.info("Pulling latest binary, version: %s", latest_version)
        tar_url = (
            f"{PROTOSTAR_REPO}/releases/download/{latest_version_tag}/{tarball_name}"
        )
        with requests.get(tar_url, stream=True) as request:
            with open(tarball_loc, "wb") as file:
                shutil.copyfileobj(request.raw, file)

    def _install_new_version(
        self, latest_version: VersionType, tarball_loc: Path, protostar_dir: Path
    ):
        self._logger.info("Installing latest Protostar version: %s", latest_version)
        with tarfile.open(tarball_loc, "r:gz") as tar:
            tar.extractall(protostar_dir)

    def _rollback(
        self, current_version: VersionType, protostar_dir: Path, old_version: Path
    ):
        self._logger.info("Rolling back to the version %s", current_version)
        shutil.rmtree(protostar_dir / "dist", ignore_errors=True)
        shutil.move(str(old_version), protostar_dir / "dist")

    def cleanup(self, old_version: Path, tarball_loc: Path):
        self._logger.info("Cleaning up after installation")
        shutil.rmtree(old_version, ignore_errors=True)
        try:
            os.remove(tarball_loc)
        except FileNotFoundError:
            pass

    @classmethod
    def get_platform(cls):
        platform = os.uname()[0]
        if platform == "Darwin":
            return "macOS"
        if platform == "Linux":
            return "Linux"
        raise UpgradeManagerException(f"{platform} is not supported")

    @classmethod
    def get_latest_release(cls):
        headers = {"Accept": "application/json"}
        response = requests.get(f"{PROTOSTAR_REPO}/releases/latest", headers=headers)
        return response.json()
