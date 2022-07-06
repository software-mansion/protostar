from dataclasses import dataclass

import requests

from protostar.utils.protostar_directory import (
    ProtostarDirectory,
    VersionManager,
    VersionType,
)


class UpgradeRemoteChecker:
    PROTOSTAR_REPO = "https://github.com/software-mansion/protostar"

    @dataclass
    class Result:
        latest_release_tag: str
        latest_version: VersionType
        is_newer_version_available: bool
        changelog_url: str

    def __init__(
        self, protostar_directory: ProtostarDirectory, version_manager: VersionManager
    ) -> None:
        self._protostar_directory = protostar_directory
        self._version_manager = version_manager

    def poll(self) -> "UpgradeRemoteChecker.Result":
        headers = {"Accept": "application/json"}
        response = requests.get(
            f"{UpgradeRemoteChecker.PROTOSTAR_REPO}/releases/latest", headers=headers
        )
        response_dict = response.json()
        latest_release_tag = response_dict["tag_name"]
        latest_version = self._version_manager.parse(latest_release_tag)
        changelog_url = "https://github.com" + response_dict["update_url"]
        return UpgradeRemoteChecker.Result(
            latest_version=latest_version,
            latest_release_tag=latest_release_tag,
            is_newer_version_available=latest_version
            > (
                self._version_manager.protostar_version
                or self._version_manager.parse("0.0.0")
            ),
            changelog_url=changelog_url,
        )
