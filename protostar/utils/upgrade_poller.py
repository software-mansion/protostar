from dataclasses import dataclass

import requests

from protostar.utils.protostar_directory import (
    ProtostarDirectory,
    VersionManager,
    VersionType,
)


class UpgradePoller:
    PROTOSTAR_REPO = "https://github.com/software-mansion/protostar"

    @dataclass
    class Result:
        latest_release_tag: str
        latest_version: VersionType
        is_newer_version_available: bool

    def __init__(
        self, protostar_directory: ProtostarDirectory, version_manager: VersionManager
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager

    def poll(self) -> "UpgradePoller.Result":
        headers = {"Accept": "application/json"}
        response = requests.get(
            f"{UpgradePoller.PROTOSTAR_REPO}/releases/latest", headers=headers
        )
        latest_release_tag = response.json()["tag_name"]
        latest_version = self._version_manager.parse(latest_release_tag)
        return UpgradePoller.Result(
            latest_version=latest_version,
            latest_release_tag=latest_release_tag,
            is_newer_version_available=latest_version
            > (
                self._version_manager.protostar_version
                or self._version_manager.parse("0.0.0")
            ),
        )
