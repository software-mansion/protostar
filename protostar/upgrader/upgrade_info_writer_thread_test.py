from typing import cast
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from protostar.upgrader.upgrade_info_writer_thread import UpgradeInfoWriterThread
from protostar.upgrader.upgrade_remote_checker import UpgradeRemoteChecker
from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils.protostar_directory import VersionManager


def test_saves_a_file_when_new_version_is_available(mocker: MockerFixture):
    remote_check_result = UpgradeRemoteChecker.Result(
        latest_version=VersionManager.parse("0.0.1"),
        latest_release_tag="v0.0.1",
        changelog_url="https://...",
        is_newer_version_available=True,
    )

    upgrade_remote_checker_mock = cast(UpgradeRemoteChecker, mocker.MagicMock())
    cast(
        MagicMock, upgrade_remote_checker_mock.check
    ).return_value = remote_check_result

    upgrade_toml_writer = cast(UpgradeTOML.Writer, mocker.MagicMock())
    upgrade_info_writer_thread = UpgradeInfoWriterThread(
        upgrade_remote_checker=upgrade_remote_checker_mock,
        upgrade_toml_writer=upgrade_toml_writer,
    )

    with upgrade_info_writer_thread:
        pass

    cast(MagicMock, upgrade_remote_checker_mock.check).assert_called_once()
    cast(MagicMock, upgrade_toml_writer.save).assert_called_once_with(
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

    upgrade_remote_checker_mock = cast(UpgradeRemoteChecker, mocker.MagicMock())
    cast(
        MagicMock, upgrade_remote_checker_mock.check
    ).return_value = remote_check_result

    upgrade_toml_writer = cast(UpgradeTOML.Writer, mocker.MagicMock())
    upgrade_info_writer_thread = UpgradeInfoWriterThread(
        upgrade_remote_checker=upgrade_remote_checker_mock,
        upgrade_toml_writer=upgrade_toml_writer,
    )

    with upgrade_info_writer_thread:
        pass

    cast(MagicMock, upgrade_remote_checker_mock.check).assert_called_once()
    cast(MagicMock, upgrade_toml_writer.save).assert_not_called()
