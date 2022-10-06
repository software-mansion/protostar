from pathlib import Path

import pytest

from protostar.configuration_file.configuration_legacy_toml_interpreter import (
    ConfigurationLegacyTOMLInterpreter,
)
from protostar.self import parse_protostar_version

from .configuration_file_v1 import (
    CommandNamesProviderProtocol,
    ConfigurationFile,
    ConfigurationFileV1,
    ConfigurationFileV1Model,
    ContractNameNotFoundException,
)


class CommandNamesProviderStub(CommandNamesProviderProtocol):
    def get_command_names(self) -> list[str]:
        return ["deploy"]


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(tmp_path: Path):
    path = tmp_path / "fake-project"
    path.mkdir()
    return path


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture():
    return ""


@pytest.fixture(name="protostar_toml_path")
def protostar_toml_path_fixture(protostar_toml_content: str, project_root_path: Path):
    path = project_root_path / "protostar.toml"
    path.write_text(protostar_toml_content)
    return path


@pytest.fixture(name="configuration_file")
def configuration_file_fixture(
    protostar_toml_path: Path, project_root_path: Path, protostar_toml_content: str
):
    cfv1 = ConfigurationFileV1(
        ConfigurationLegacyTOMLInterpreter(
            file_content=protostar_toml_content,
        ),
        project_root_path=project_root_path,
        file_path=protostar_toml_path,
    )
    cfv1.set_command_names_provider(CommandNamesProviderStub())
    return cfv1


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.config"]
        protostar_version = "0.1.2"
        """,
    ],
)
def test_retrieving_declared_protostar_version(configuration_file: ConfigurationFile):
    result = configuration_file.get_declared_protostar_version()

    assert result == parse_protostar_version("0.1.2")


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.contracts"]
        main = [
        "./src/main.cairo",
        ]
        foo = [
        "./src/foo.cairo",
        ]
        """
    ],
)
def test_retrieving_contract_names(configuration_file: ConfigurationFile):
    contract_names = configuration_file.get_contract_names()

    assert contract_names == ["main", "foo"]


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.contracts"]
        main = [
        "./src/main.cairo",
        ]
        foo = [
        "./src/foo.cairo",
        "./src/bar.cairo",
        ]
        """
    ],
)
def test_retrieving_contract_source_paths(
    configuration_file: ConfigurationFile, project_root_path: Path
):
    paths = configuration_file.get_contract_source_paths(contract_name="foo")

    assert paths == [
        (project_root_path / "./src/foo.cairo").resolve(),
        (project_root_path / "./src/bar.cairo").resolve(),
    ]


def test_error_when_retrieving_paths_from_not_defined_contract(
    configuration_file: ConfigurationFile,
):
    with pytest.raises(ContractNameNotFoundException):
        configuration_file.get_contract_source_paths(
            contract_name="NOT_DEFINED_CONTRACT"
        )


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.project"]
        libs_path = "./lib"
        """
    ],
)
def test_reading_lib_path(
    configuration_file: ConfigurationFileV1, project_root_path: Path
):
    lib_path = configuration_file.get_lib_path()

    assert lib_path is not None
    assert lib_path == (project_root_path / "lib").resolve()


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.command_name"]
        arg_name = 42
        """
    ],
)
def test_reading_command_argument_attribute(configuration_file: ConfigurationFile):
    arg_value = configuration_file.get_argument_value(
        command_name="command_name", argument_name="arg_name"
    )

    assert arg_value == 42


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.command_name"]
        arg_name = 21

        ["profile.devnet.protostar.command_name"]
        arg_name = 37
        """
    ],
)
def test_reading_argument_attribute_defined_within_specified_profile(
    configuration_file: ConfigurationFile,
):
    arg_value = configuration_file.get_argument_value(
        command_name="command_name", argument_name="arg_name", profile_name="devnet"
    )

    assert arg_value == 37


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.shared_command_configs"]
        arg_name = 21

        ["profile.profile_name.protostar.shared_command_configs"]
        arg_name = 37
        """
    ],
)
def test_reading_shared_argument_value(configuration_file: ConfigurationFileV1):
    assert configuration_file.get_shared_argument_value(argument_name="arg_name") == 21
    assert (
        configuration_file.get_shared_argument_value(
            argument_name="arg_name", profile_name="profile_name"
        )
        == 37
    )


@pytest.mark.parametrize(
    "protostar_toml_content",
    [
        """
        ["protostar.config"]
        protostar_version = "0.3.1"

        ["protostar.project"]
        libs_path = "./lib"

        ["protostar.contracts"]
        main = [
            "./src/main.cairo",
        ]

        ["protostar.deploy"]
        arg_name = 21

        ["profile.devnet.protostar.deploy"]
        arg_name = 37

        ["protostar.shared_command_configs"]
        arg_name = 42

        ["profile.devnet.protostar.shared_command_configs"]
        arg_name = 24
        """
    ],
)
def test_generating_data_struct(
    configuration_file: ConfigurationFileV1,
):
    model = configuration_file.read()

    assert model == ConfigurationFileV1Model(
        protostar_version="0.3.1",
        libs_path_str="lib",
        command_name_to_config={"deploy": {"arg_name": 21}},
        contract_name_to_path_strs={"main": ["src/main.cairo"]},
        shared_command_config={"arg_name": 42},
        profile_name_to_commands_config={"devnet": {"deploy": {"arg_name": 37}}},
        profile_name_to_shared_command_config={"devnet": {"arg_name": 24}},
    )
