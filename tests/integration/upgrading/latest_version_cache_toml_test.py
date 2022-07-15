from datetime import datetime
from pathlib import Path

from pytest_mock import MockerFixture

from protostar.upgrader.latest_version_cache_toml import LatestVersionCacheTOML
from protostar.utils.protostar_directory import VersionManager


def test_latest_version_cache_toml_saving_and_loading(
    mocker: MockerFixture, tmp_path: Path
):
    latest_version_cache_toml = LatestVersionCacheTOML(
        changelog_url="https://...",
        version=VersionManager.parse("0.0.0"),
        next_check_datetime=datetime(year=2022, month=1, day=1),
    )
    protostar_directory_mock = mocker.MagicMock()
    protostar_directory_mock.latest_version_cache_path = (
        tmp_path / "latest_version_cache.toml"
    )

    LatestVersionCacheTOML.Writer(protostar_directory_mock).save(
        latest_version_cache_toml
    )
    loaded_latest_version_cache_toml = LatestVersionCacheTOML.Reader(
        protostar_directory_mock
    ).read()

    assert latest_version_cache_toml == loaded_latest_version_cache_toml
