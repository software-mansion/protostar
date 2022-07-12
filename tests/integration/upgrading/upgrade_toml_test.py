from datetime import datetime
from pathlib import Path

from pytest_mock import MockerFixture

from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils.protostar_directory import VersionManager


def test_upgrade_toml_saving_and_loading(mocker: MockerFixture, tmp_path: Path):
    upgrade_toml = UpgradeTOML(
        changelog_url="https://...",
        version=VersionManager.parse("0.0.0"),
        next_check_datetime=datetime(year=2022, month=1, day=1),
    )
    protostar_directory_mock = mocker.MagicMock()
    protostar_directory_mock.upgrade_toml_path = tmp_path / "upgrade.toml"

    UpgradeTOML.Writer(protostar_directory_mock).save(upgrade_toml)
    loaded_upgrade_toml = UpgradeTOML.Reader(protostar_directory_mock).read()

    assert upgrade_toml == loaded_upgrade_toml
