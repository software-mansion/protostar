from pathlib import Path
from typing import Dict

import pytest

from protostar.protostar_toml.conftest import MockProtostarTOMLReaderFixture
from protostar.protostar_toml.protostar_project_section import \
    ProtostarProjectSection
from protostar.protostar_toml.protostar_toml_exceptions import \
    InvalidProtostarTOMLException


@pytest.fixture(name="section_dict")
def section_dict_fixture() -> Dict:
    return {"libs_path": "lib"}


def test_serialization(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture, section_dict: Dict
):
    protostar_toml_reader_mock = mock_protostar_toml_reader(section_dict)

    section = ProtostarProjectSection.load(protostar_toml_reader_mock)

    assert section.libs_path == Path("lib")
    assert section.to_dict() == section_dict


def test_fail_loading_libs_path(
    mock_protostar_toml_reader: MockProtostarTOMLReaderFixture,
):
    protostar_toml_reader_mock = mock_protostar_toml_reader(
        protostar_section_dict="True"
    )

    with pytest.raises(InvalidProtostarTOMLException):
        ProtostarProjectSection.load(protostar_toml_reader_mock)
