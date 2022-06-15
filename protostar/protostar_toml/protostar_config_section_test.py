import pytest

from protostar.protostar_toml.conftest import MockProtostarTOMLReaderFixture
from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)
from protostar.utils.protostar_directory import VersionManager


@pytest.fixture(name="protostar_config_section_dict")
def protostar_config_section_dict_fixture() -> ProtostarConfigSection.ParsedProtostarTOML:
    return {"protostar_version": "0.1.0"}


def test_serialization(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture,
    protostar_config_section_dict,
):
    protostar_toml_mock = mock_protostar_toml_reader(protostar_config_section_dict)

    config_section = ProtostarConfigSection.from_protostar_toml_reader(
        protostar_toml_mock
    )

    assert config_section.protostar_version == VersionManager.parse("0.1.0")
    assert config_section.to_dict() == protostar_config_section_dict


def test_fail_on_loading_undefined_section(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture,
):
    protostar_toml_mock = mock_protostar_toml_reader(protostar_section_dict=None)

    with pytest.raises(InvalidProtostarTOMLException):
        ProtostarConfigSection.from_protostar_toml_reader(protostar_toml_mock)


def test_fail_on_loading_corrupted_protostar_version(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture,
):
    protostar_toml_mock = mock_protostar_toml_reader({"protostar_version": 42})

    with pytest.raises(InvalidProtostarTOMLException):
        ProtostarConfigSection.from_protostar_toml_reader(protostar_toml_mock)
