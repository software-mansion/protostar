from typing import Any

from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader


def mock_protostar_toml_reader(mocker: MockerFixture):
    def mock(protostar_section_dict: Any) -> ProtostarTOMLReader:
        protostar_toml_reader_mock = mocker.MagicMock
        protostar_toml_reader_mock.get_section = mocker.MagicMock()
        protostar_toml_reader_mock.get_section.return_value = protostar_section_dict
        return protostar_toml_reader_mock

    return mock
