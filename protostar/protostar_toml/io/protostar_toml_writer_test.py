from pytest_mock import MockerFixture
from py._path.local import LocalPath

from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection


def test_saving_configuration_file(tmpdir: LocalPath, mocker: MockerFixture):
    version_manager_mock = mocker.MagicMock()
    version_manager_mock.protostar_version = "0.1.0"

    path = tmpdir / "protostar.toml"
    ProtostarTOMLWriter().save(
        path,
        protostar_config=ProtostarConfigSection.get_default(version_manager_mock),
        protostar_project=ProtostarProjectSection.get_default(),
        protostar_contracts=ProtostarContractsSection.get_default(),
    )

    with open(path, "r", encoding="utf-8") as protostar_toml_file:
        protostar_toml_content = protostar_toml_file.read()
        assert '["protostar.config"]' in protostar_toml_content
        assert 'protostar_version = "0.1.0"' in protostar_toml_content

        assert '["protostar.project"]' in protostar_toml_content
        assert 'libs_path = "lib"' in protostar_toml_content
