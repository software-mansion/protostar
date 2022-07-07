import asyncio
from typing import cast
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

# pylint: disable=redefined-builtin
from requests.exceptions import ConnectionError

from protostar.upgrader.upgrade_info_writer_thread import UpgradeInfoWriterThread
from protostar.upgrader.upgrade_remote_checker import UpgradeRemoteChecker
from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils.protostar_directory import VersionManager


async def test_saves_a_file_when_new_version_is_available(mocker: MockerFixture):
    remote_check_result = UpgradeRemoteChecker.Result(
        latest_version=VersionManager.parse("0.0.1"),
        latest_release_tag="v0.0.1",
        changelog_url="https://...",
        is_newer_version_available=True,
    )

    async def check_mock():
        return remote_check_result

    upgrade_remote_checker_mock = cast(UpgradeRemoteChecker, mocker.MagicMock())
    upgrade_remote_checker_mock.check = check_mock

    upgrade_toml_writer_mock = cast(UpgradeTOML.Writer, mocker.MagicMock())
    upgrade_info_writer_thread = UpgradeInfoWriterThread(
        upgrade_remote_checker=upgrade_remote_checker_mock,
        upgrade_toml_writer=upgrade_toml_writer_mock,
    )

    with upgrade_info_writer_thread:
        await asyncio.sleep(0.1)

    cast(MagicMock, upgrade_toml_writer_mock.save).assert_called_once_with(
        UpgradeTOML(
            version=remote_check_result.latest_version,
            changelog_url=remote_check_result.changelog_url,
        )
    )


def test_not_saves_a_file_when_new_version_is_not_available(mocker: MockerFixture):
    remote_check_result = UpgradeRemoteChecker.Result(
        latest_version=VersionManager.parse("0.0.1"),
        latest_release_tag="v0.0.1",
        changelog_url="https://...",
        is_newer_version_available=False,
    )

    async def check_mock():
        return remote_check_result

    upgrade_remote_checker_mock = cast(UpgradeRemoteChecker, mocker.MagicMock())
    upgrade_remote_checker_mock.check = check_mock

    upgrade_toml_writer_mock = cast(UpgradeTOML.Writer, mocker.MagicMock())
    upgrade_info_writer_thread = UpgradeInfoWriterThread(
        upgrade_remote_checker=upgrade_remote_checker_mock,
        upgrade_toml_writer=upgrade_toml_writer_mock,
    )

    with upgrade_info_writer_thread:
        pass

    cast(MagicMock, upgrade_toml_writer_mock.save).assert_not_called()


def test_does_not_fail_when_there_is_no_connection(mocker: MockerFixture):
    upgrade_remote_checker_mock = cast(UpgradeRemoteChecker, mocker.MagicMock())
    cast(MagicMock, upgrade_remote_checker_mock.check).side_effect = ConnectionError()
    upgrade_toml_writer_mock = mocker.MagicMock()
    upgrade_info_writer_thread = UpgradeInfoWriterThread(
        upgrade_remote_checker=upgrade_remote_checker_mock,
        upgrade_toml_writer=upgrade_toml_writer_mock,
    )

    upgrade_info_writer_thread.check_new_version_safely()

    assert True
