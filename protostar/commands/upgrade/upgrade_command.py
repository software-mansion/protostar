# pylint: disable=broad-except
import os
import shutil
import tarfile
from logging import getLogger
from typing import List, Optional
from urllib.request import urlretrieve

import requests
from packaging import version

from protostar.cli.command import Command
from protostar.utils import ProtostarDirectory, VersionManager

logger = getLogger()

PROTOSTAR_REPO = "https://github.com/software-mansion/protostar"


class UpgradeCommand(Command):
    def __init__(
        self, protostar_directory: ProtostarDirectory, version_manager: VersionManager
    ) -> None:
        super().__init__()
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager

    @property
    def name(self) -> str:
        return "upgrade"

    @property
    def description(self) -> str:
        return "Upgrade Protostar."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar upgrade"

    @property
    def arguments(self) -> List[Command.Argument]:
        return []

    async def run(self, _args):
        upgrade(self._protostar_directory, self._version_manager)


def upgrade(
    protostar_directory: ProtostarDirectory, version_manager: VersionManager
) -> None:
    manager = UpgradeManager(protostar_directory, version_manager)
    manager.upgrade()


class UpgradeManagerException(Exception):
    pass


class UpgradeManager:
    def __init__(
        self, protostar_directory: ProtostarDirectory, version_manager: VersionManager
    ):
        assert os.path.isdir(protostar_directory.directory_root_path)
        assert os.path.isdir(protostar_directory.directory_root_path / "dist")
        self.protostar_dir = protostar_directory.directory_root_path
        self.old_version = self.protostar_dir / "previous_version_tmp"

        platform = self.get_platform()
        self.tarball_name = f"protostar-{platform}.tar.gz"
        self.tarball_loc = self.protostar_dir / self.tarball_name

        self.current_version = (
            version_manager.protostar_version or VersionManager.parse("0.0.0")
        )
        self.latest_version_tag = self.get_latest_release()["tag_name"]
        self.latest_version = version.parse(self.latest_version_tag)

    def is_current_latest(self):
        return self.latest_version == self.current_version

    def upgrade(self):
        logger.info("Looking for a new version ...")
        if self.latest_version <= self.current_version:
            logger.info("Protostar is up to date")
            return

        logger.info(
            "Starting upgrade from version %s to version %s",
            self.current_version,
            self.latest_version,
        )
        self._backup()
        try:
            self._pull_tarball()
            self._install_new_version()
            self.cleanup()
        except KeyboardInterrupt:
            logger.info("Interrupting...")
            self._rollback()
            self.cleanup()
        except (Exception, SystemExit) as err:
            self._handle_error(err)

    def _handle_error(self, err):
        logger.error(
            (
                "Upgrade failed\n"
                "You can run the following installation script instead:\n"
                "curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash"
            )
        )
        self._rollback()
        self.cleanup()
        raise err

    def _backup(self):
        shutil.move(str(self.protostar_dir / "dist"), self.old_version)

    def _pull_tarball(self):
        logger.info("Pulling latest binary, version: %s", self.latest_version)
        tar_url = f"{PROTOSTAR_REPO}/releases/download/{self.latest_version_tag}/{self.tarball_name}"
        with requests.get(tar_url, stream=True) as r:
            with open(self.tarball_loc, 'wb') as f:
                shutil.copyfileobj(r.raw, f)



    def _install_new_version(self):
        logger.info("Installing latest Protostar version: %s", self.latest_version)
        with tarfile.open(self.tarball_loc, "r:gz") as tar:
            tar.extractall(self.protostar_dir)

    def _rollback(self):
        logger.info("Rolling back to the version %s", self.current_version)
        shutil.rmtree(self.protostar_dir / "dist", ignore_errors=True)
        shutil.move(str(self.old_version), self.protostar_dir / "dist")

    def cleanup(self):
        logger.info("Cleaning up after installation")
        shutil.rmtree(self.old_version, ignore_errors=True)
        try:
            os.remove(self.tarball_loc)
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
