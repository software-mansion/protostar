import textwrap
from pathlib import Path

import pytest

from protostar.configuration_file.configuration_toml_content_builder import (
    ConfigurationTOMLContentBuilder,
)
from protostar.configuration_file.configuration_toml_interpreter import (
    ConfigurationTOMLInterpreter,
)
from protostar.self import parse_protostar_version

from .configuration_file import (
    ConfigurationFile,
    ConfigurationFileContentConfigurator,
    ContractNameNotFoundException,
)
from .configuration_file_v1 import (
    CommandNamesProviderProtocol,
    ConfigurationFileV1,
    ConfigurationFileV1Model,
)
from .configuration_file_v2 import ConfigurationFileV2, ConfigurationFileV2Model
from .configuration_legacy_toml_interpreter import ConfigurationLegacyTOMLInterpreter


class CommandNamesProviderDouble(CommandNamesProviderProtocol):
    def get_command_names(self) -> list[str]:
        return ["declare"]


@pytest.fixture(name="protostar_toml_content")
def protostar_toml_content_fixture() -> str:
    return textwrap.dedent(
        """\
        [project]
        protostar-version = "9.9.9"
        lib-path = "lib"
        no-color = true
        network = "devnet1"
        cairo-path = ["bar"]

        [contracts]
        foo = ["src/foo.cairo"]
        bar = ["src/bar.cairo"]

        [declare]
        network = "devnet2"

        [profile.release.project]
        network = "mainnet2"

        [profile.release.declare]
        network = "mainnet"
    """
    )


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(tmp_path: Path):
    return tmp_path


@pytest.fixture(name="configuration_file")
def configuration_file_fixture(project_root_path: Path, protostar_toml_content: str):
    protostar_toml_path = project_root_path / "protostar.toml"
    protostar_toml_path.write_text(protostar_toml_content)
    configuration_toml_reader = ConfigurationLegacyTOMLInterpreter(
        file_content=protostar_toml_content
    )
    return ConfigurationFileV2(
        project_root_path=project_root_path,
        configuration_file_interpreter=configuration_toml_reader,
        filename=protostar_toml_path.name,
    )


def test_retrieving_declared_protostar_version(configuration_file: ConfigurationFile):
    declared_protostar_version = configuration_file.get_declared_protostar_version()

    assert declared_protostar_version == parse_protostar_version("9.9.9")


def test_retrieving_contract_names(configuration_file: ConfigurationFile):
    contract_names = configuration_file.get_contract_names()

    assert contract_names == ["foo", "bar"]


def test_retrieving_contract_source_paths(
    configuration_file: ConfigurationFileV2, project_root_path: Path
):
    paths = configuration_file.get_contract_source_paths(contract_name="foo")

    assert paths == [
        (project_root_path / "./src/foo.cairo").resolve(),
    ]


def test_error_when_retrieving_paths_from_not_defined_contract(
    configuration_file: ConfigurationFileV2,
):
    with pytest.raises(ContractNameNotFoundException):
        configuration_file.get_contract_source_paths(
            contract_name="NOT_DEFINED_CONTRACT"
        )


def test_reading_command_argument_attribute(configuration_file: ConfigurationFile):
    arg_value = configuration_file.get_command_argument(
        command_name="declare", argument_name="network"
    )

    assert arg_value == "devnet2"


def test_reading_argument_attribute_defined_within_specified_profile(
    configuration_file: ConfigurationFile,
):
    arg_value = configuration_file.get_command_argument(
        command_name="declare", argument_name="network", profile_name="release"
    )

    assert arg_value == "mainnet"


def test_saving_configuration(
    configuration_file: ConfigurationFileContentConfigurator[ConfigurationFileV2Model],
    protostar_toml_content: str,
):
    content_configurator = configuration_file
    configuration_file_v2_model = ConfigurationFileV2Model(
        protostar_version="9.9.9",
        project_config={
            "lib-path": "lib",
            "no-color": True,
            "network": "devnet1",
            "cairo-path": ["bar"],
        },
        command_name_to_config={"declare": {"network": "devnet2"}},
        contract_name_to_path_strs={
            "foo": [
                "src/foo.cairo",
            ],
            "bar": [
                "src/bar.cairo",
            ],
        },
        profile_name_to_commands_config={
            "release": {"declare": {"network": "mainnet"}}
        },
        profile_name_to_project_config={"release": {"network": "mainnet2"}},
    )

    result = content_configurator.create_file_content(
        model=configuration_file_v2_model,
        content_builder=ConfigurationTOMLContentBuilder(),
    )

    assert result == protostar_toml_content


def test_transforming_model_v1_into_v2():
    model_v1 = ConfigurationFileV1Model(
        protostar_version="0.3.1",
        libs_path_str="lib",
        command_name_to_config={"deploy": {"arg_name": 21}},
        contract_name_to_path_strs={"main": ["src/main.cairo"]},
        shared_command_config={"arg_name": 42},
        profile_name_to_commands_config={"devnet": {"deploy": {"arg_name": 37}}},
        profile_name_to_shared_command_config={"devnet": {"arg_name": 24}},
    )

    model_v2 = ConfigurationFileV2Model.from_v1(model_v1, protostar_version="0.4.0")

    assert model_v2 == ConfigurationFileV2Model(
        protostar_version="0.4.0",
        command_name_to_config={"deploy": {"arg_name": 21}},
        contract_name_to_path_strs={"main": ["src/main.cairo"]},
        project_config={"arg_name": 42, "lib-path": "lib"},
        profile_name_to_commands_config={"devnet": {"deploy": {"arg_name": 37}}},
        profile_name_to_project_config={"devnet": {"arg_name": 24}},
    )


def test_transforming_file_v1_into_v2(protostar_toml_content: str):
    old_protostar_toml_content = textwrap.dedent(
        """\
        ["protostar.config"]
        protostar_version = "0.3.0"

        ["protostar.project"]
        libs_path = "./lib"

        ["protostar.contracts"]
        foo = [
            "./src/foo.cairo",
        ]
        bar = [
            "./src/bar.cairo",
        ]

        ["protostar.shared_command_configs"]
        no-color = true
        network = "devnet1"
        cairo-path = [
            "bar",
        ]

        ["protostar.declare"]
        network = "devnet2"

        ["profile.release.protostar.shared_command_configs"]
        network = "mainnet2"

        ["profile.release.protostar.declare"]
        network = "mainnet"
        """
    )

    model_v1 = ConfigurationFileV1(
        configuration_file_interpreter=ConfigurationLegacyTOMLInterpreter(
            file_content=old_protostar_toml_content,
        ),
        project_root_path=Path(),
        filename="_",
        command_names_provider=CommandNamesProviderDouble(),
    ).read()

    transformed_protostar_toml = ConfigurationFileV2(
        configuration_file_interpreter=ConfigurationTOMLInterpreter(
            file_content=old_protostar_toml_content,
        ),
        project_root_path=Path(),
        filename="_",
    ).create_file_content(
        content_builder=ConfigurationTOMLContentBuilder(),
        model=ConfigurationFileV2Model.from_v1(model_v1, protostar_version="9.9.9"),
    )

    assert transformed_protostar_toml == protostar_toml_content


def test_saving_in_particular_order(
    configuration_file: ConfigurationFileContentConfigurator[ConfigurationFileV2Model],
):
    content_configurator = configuration_file
    configuration_file_v2_model = ConfigurationFileV2Model(
        protostar_version="9.9.9",
        project_config={
            "lib-path": "./lib",
            "cairo-path": ["bar"],
            "no-color": True,
            "network": "devnet1",
        },
        command_name_to_config={},
        contract_name_to_path_strs={},
        profile_name_to_commands_config={},
        profile_name_to_project_config={},
    )

    result = content_configurator.create_file_content(
        content_builder=ConfigurationTOMLContentBuilder(),
        model=configuration_file_v2_model,
    )

    assert result.index("[project]") < result.index("[contracts]")
    assert result.index("lib-path") < result.index("cairo-path")
    assert result.index("cairo-path") < result.index("no-color")
    assert result.index("no-color") < result.index("network")
