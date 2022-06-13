from pathlib import Path
from typing import Dict

import pytest
from pytest_mock import MockerFixture

from protostar.protostar_toml._conftest import mock_protostar_toml_reader
from protostar.protostar_toml.protostar_project_section import \
    ProtostarProjectSection
from protostar.protostar_toml.protostar_toml_exceptions import \
    InvalidProtostarTOMLException


@pytest.fixture(name="section_dict")
def section_dict_fixture() -> Dict:
    return {"libs_path": "lib"}


def test_serialization(mocker: MockerFixture, section_dict: Dict):
    protostar_toml_reader_mock = mock_protostar_toml_reader(mocker)(section_dict)

    section = ProtostarProjectSection.from_protostar_toml(protostar_toml_reader_mock)

    assert section.libs_path == Path("lib")
    assert section.to_dict() == section_dict


def test_fail_loading_libs_path(mocker: MockerFixture):
    protostar_toml_reader_mock = mock_protostar_toml_reader(mocker)(
        protostar_section_dict=None
    )

    with pytest.raises(InvalidProtostarTOMLException):
        ProtostarProjectSection.from_protostar_toml(protostar_toml_reader_mock)
