from typing import cast

import pytest
from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_toml_exceptions import (
    InvalidProtostarTOMLException,
)
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils.protostar_directory import VersionManager


@pytest.fixture(name="protostar_config_section_dict")
def protostar_config_section_dict_fixture() -> ProtostarConfigSection.TOMLCompatibleDict:
    return {"protostar_version": "0.1.0"}


def test_loading_and_writing_section(
    mocker: MockerFixture,
    protostar_config_section_dict,
):
    protostar_toml_mock = cast(ProtostarTOMLReader, mocker.MagicMock)
    protostar_toml_mock.get_section = mocker.MagicMock()
    protostar_toml_mock.get_section.return_value = protostar_config_section_dict

    config_section = ProtostarConfigSection.from_protostar_toml_reader(
        protostar_toml_mock
    )

    assert config_section.protostar_version == VersionManager.parse("0.1.0")
    assert config_section.to_dict() == protostar_config_section_dict


def test_fail_on_loading_undefined_section(mocker: MockerFixture):
    protostar_toml_mock = cast(ProtostarTOMLReader, mocker.MagicMock)
    protostar_toml_mock.get_section = mocker.MagicMock()
    protostar_toml_mock.get_section.return_value = None

    with pytest.raises(InvalidProtostarTOMLException):
        ProtostarConfigSection.from_protostar_toml_reader(protostar_toml_mock)


def test_fail_on_loading_corrupted_protostar_version(mocker: MockerFixture):
    protostar_toml_mock = cast(ProtostarTOMLReader, mocker.MagicMock)
    protostar_toml_mock.get_section = mocker.MagicMock()
    protostar_toml_mock.get_section.return_value = {"protostar_version": 42}

    with pytest.raises(InvalidProtostarTOMLException):
        ProtostarConfigSection.from_protostar_toml_reader(protostar_toml_mock)
