from pytest_mock import MockerFixture

from protostar.upgrader.latest_version_remote_checker import LatestVersionRemoteChecker
from protostar.utils.protostar_directory import VersionManager


async def test_upgrade_remote_checker(mocker: MockerFixture):
    version_manager_mock = mocker.MagicMock()
    version_manager_mock.protostar_version = VersionManager.parse("0.0.0")
    upgrade_remote_checker = LatestVersionRemoteChecker(
        version_manager=version_manager_mock
    )

    result = await upgrade_remote_checker.check()

    assert result.changelog_url.startswith(
        "https://github.com/software-mansion/protostar/releases/tag"
    )
    assert result.is_newer_version_available is True
