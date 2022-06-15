from typing import Any

import pytest
from pytest_mock import MockerFixture
from typing_extensions import Protocol

from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader


class MockProtostarTOMLReaderFixture(Protocol):
    def __call__(self, protostar_section_dict: Any) -> ProtostarTOMLReader:
        ...


@pytest.fixture(name="mock_protostar_toml_reader")
def mock_protostar_toml_reader(mocker: MockerFixture) -> MockProtostarTOMLReaderFixture:
    def mock(protostar_section_dict: Any) -> ProtostarTOMLReader:
        protostar_toml_reader_mock = mocker.MagicMock
        protostar_toml_reader_mock.get_section = mocker.MagicMock()
        protostar_toml_reader_mock.get_section.return_value = protostar_section_dict
        return protostar_toml_reader_mock

    return mock
