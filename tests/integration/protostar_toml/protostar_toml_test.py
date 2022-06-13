from pathlib import Path

from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_writer import ProtostarTOMLWriter
from protostar.utils.protostar_directory import VersionManager


def test_saving_and_reading(tmpdir, mocker: MockerFixture):
    version_manager_mock = mocker.MagicMock()
    version_manager_mock.protostar_version = VersionManager.parse("0.1.0")

    path = Path(tmpdir) / "protostar.toml"
    ProtostarTOMLWriter().save_default(path, version_manager=version_manager_mock)

    reader = ProtostarTOMLReader(path)
    assert reader.get_attribute("config", "protostar_version") == "0.1.0"
    assert reader.get_attribute("project", "libs_path") == "lib"
    assert reader.get_attribute("contracts", "main") == ["src/main.cairo"]
