from pathlib import Path

from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.protostar_toml.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.protostar_toml_writer import ProtostarTOMLWriter
from protostar.utils.protostar_directory import VersionManager


def test_saving_and_reading(tmpdir, mocker: MockerFixture):
    version_manager_mock = mocker.MagicMock()
    version_manager_mock.protostar_version = VersionManager.parse("0.1.0")
    path = Path(tmpdir) / "protostar.toml"
    config_section = ProtostarConfigSection.get_default(version_manager_mock)
    project_section = ProtostarProjectSection.get_default()
    contracts_section = ProtostarContractsSection.get_default()

    ProtostarTOMLWriter().save(
        path,
        config_section,
        project_section,
        contracts_section,
    )
    reader = ProtostarTOMLReader(path)

    assert (
        ProtostarConfigSection.from_protostar_toml_reader(reader).protostar_version
        == config_section.protostar_version
    )
    assert (
        ProtostarProjectSection.from_protostar_toml(reader).libs_path
        == project_section.libs_path
    )
    assert (
        ProtostarContractsSection.from_protostar_toml_reader(
            reader
        ).contract_name_to_paths
        == contracts_section.contract_name_to_paths
    )
