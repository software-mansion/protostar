from pathlib import Path
from typing import Optional

import pytest

from protostar.configuration_file.configuration_toml_interpreter import (
    ConfigurationTOMLInterpreter,
)

from .configuration_toml_content_builder import ConfigurationTOMLContentBuilder
from .configuration_file_v2 import (
    ConfigurationFileV2Model,
    ConfigurationFileV2ContentFactory,
    ConfigurationFileV2,
)


def create_configuration_file_v2(
    model: ConfigurationFileV2Model, profile_name: Optional[str]
):
    file_content = ConfigurationFileV2ContentFactory(
        content_builder=ConfigurationTOMLContentBuilder()
    ).create_file_content(model)
    return ConfigurationFileV2(
        configuration_file_interpreter=ConfigurationTOMLInterpreter(
            file_content=file_content,
        ),
        file_path=Path(),
        project_root_path=Path(),
        active_profile_name=profile_name,
    )


@pytest.mark.parametrize("profile_name", [None, "PROFILE_NAME"])
def test_loading_shared_argument_when_profile_is_provided(profile_name: Optional[str]):
    # https://github.com/software-mansion/protostar/issues/1181
    configuration_file_v2 = create_configuration_file_v2(
        ConfigurationFileV2Model(
            command_name_to_config={},
            contract_name_to_path_strs={},
            profile_name_to_commands_config={
                "PROFILE_NAME": {"test": {"target": ["TARGET"]}}
            },
            profile_name_to_project_config={},
            project_config={"cairo-path": ["CAIRO_PATH"]},
            protostar_version=None,
        ),
        profile_name=profile_name,
    )

    arg_value = configuration_file_v2.resolve_argument(
        command_name="test", argument_name="cairo-path"
    )

    assert arg_value == ["CAIRO_PATH"]
