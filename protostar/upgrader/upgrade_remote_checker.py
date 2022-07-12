from dataclasses import dataclass

import requests

from protostar.utils.protostar_directory import VersionManager, VersionType


class UpgradeRemoteChecker:
    """
    Call a remote endpoint to figure out if the new Protostar version is available.
    """

    PROTOSTAR_REPO = "https://github.com/software-mansion/protostar"

    @dataclass
    class Result:
        latest_release_tag: str
        latest_version: VersionType
        is_newer_version_available: bool
        changelog_url: str

    def __init__(self, version_manager: VersionManager) -> None:
        self._version_manager = version_manager

    async def check(self) -> "UpgradeRemoteChecker.Result":
        headers = {"Accept": "application/json"}
        response = requests.get(
            f"{UpgradeRemoteChecker.PROTOSTAR_REPO}/releases/latest",
            headers=headers,
            timeout=8,
        )
        response_dict = response.json()
        latest_release_tag = response_dict["tag_name"]
        latest_version = VersionManager.parse(latest_release_tag)
        changelog_url = "https://github.com" + response_dict["update_url"]
        return UpgradeRemoteChecker.Result(
            latest_version=latest_version,
            latest_release_tag=latest_release_tag,
            is_newer_version_available=latest_version
            > (
                self._version_manager.protostar_version or VersionManager.parse("0.0.0")
            ),
            changelog_url=changelog_url,
        )
