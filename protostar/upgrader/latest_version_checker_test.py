from datetime import datetime, timedelta
from logging import Logger
from typing import Any, cast

import pytest
from pytest_mock import MockerFixture

from protostar.upgrader.latest_version_cache_toml import LatestVersionCacheTOML
from protostar.upgrader.latest_version_checker import LatestVersionChecker
from protostar.utils.log_color_provider import LogColorProvider
from protostar.utils.protostar_directory import ProtostarDirectory, VersionManager


@pytest.fixture(name="log_color_provider_mock")
def log_color_provider_mock_fixture(mocker: MockerFixture):
    log_color_provider_mock = cast(LogColorProvider, mocker.MagicMock())

    def colorize(_: str, content: str) -> str:
        return content

    cast(mocker.MagicMock, log_color_provider_mock).colorize = colorize
    return log_color_provider_mock


async def test_logs_info_about_new_version_when_protostar_is_not_up_to_date(
    mocker: MockerFixture, log_color_provider_mock
):
    logger_mock = cast(Logger, mocker.MagicMock())
    protostar_directory_mock = cast(ProtostarDirectory, mocker.MagicMock())
    version_manager_mock = cast(VersionManager, mocker.MagicMock())
    latest_version_cache_toml_reader_mock = cast(
        LatestVersionCacheTOML.Reader, mocker.MagicMock()
    )

    upgrade_toml = LatestVersionCacheTOML(
        version=VersionManager.parse("0.1.0"),
        changelog_url="https://...",
        next_check_datetime=datetime.now() + timedelta(days=4),
    )
    cast(
        mocker.MagicMock, latest_version_cache_toml_reader_mock.read
    ).return_value = upgrade_toml
    cast(Any, version_manager_mock).protostar_version = VersionManager.parse("0.0.0")

    upgrade_local_checker = LatestVersionChecker(
        log_color_provider=log_color_provider_mock,
        logger=logger_mock,
        protostar_directory=protostar_directory_mock,
        version_manager=version_manager_mock,
        latest_version_cache_toml_reader=latest_version_cache_toml_reader_mock,
        latest_version_remote_checker=mocker.MagicMock(),
        latest_version_cache_toml_writer=mocker.MagicMock(),
    )

    await upgrade_local_checker.run()

    assert (
        "new Protostar version"
        in cast(mocker.MagicMock, logger_mock.info).call_args_list[0][0][0]
    )
