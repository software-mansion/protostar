from typing import cast

from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils.protostar_directory import VersionManager


def test_loading_data(mocker: MockerFixture):
    protostar_toml_mock = cast(ProtostarTOMLReader, mocker.MagicMock)
    protostar_toml_mock.get_section = mocker.MagicMock()
    protostar_toml_mock.get_section.return_value = {"protostar_version": "0.1.0"}

    config_section = ProtostarConfigSection.from_protostar_toml_reader(
        protostar_toml_mock
    )

    assert config_section.protostar_version == VersionManager.parse("0.1.0")
