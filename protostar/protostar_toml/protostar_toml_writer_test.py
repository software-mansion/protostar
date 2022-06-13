from pytest_mock import MockerFixture

from protostar.protostar_toml.protostar_toml_writer import ProtostarTOMLWriter


def test_saving_default_configuration_file(tmpdir, mocker: MockerFixture):
    version_manager_mock = mocker.MagicMock()
    version_manager_mock.protostar_version = "0.1.0"

    path = tmpdir / "protostar.toml"
    ProtostarTOMLWriter().save_default(path, version_manager=version_manager_mock)

    with open(path, "r", encoding="utf-8") as protostar_toml_file:
        protostar_toml_content = protostar_toml_file.read()
        assert '["protostar.config"]' in protostar_toml_content
        assert 'protostar_version = "0.1.0"' in protostar_toml_content

        assert '["protostar.project"]' in protostar_toml_content
        assert 'libs_path = "lib"' in protostar_toml_content
