from pathlib import Path
from typing import Optional

import pytest
from pytest_mock import MockerFixture

from protostar.cli.argument_value_from_config_provider import (
    ArgumentValueFromConfigProvider,
)
from protostar.utils import Project


@pytest.fixture(name="configuration_profile_name")
def configuration_profile_name_fixture() -> Optional[str]:
    return None


@pytest.fixture(name="arg_value_provider")
def arg_value_provider_fixture(
    mocker: MockerFixture, datadir: Path, configuration_profile_name
):
    return ArgumentValueFromConfigProvider(
        Project(project_root=datadir, version_manager=mocker.MagicMock()),
        configuration_profile_name,
    )


@pytest.mark.parametrize("configuration_profile_name", [None])
def test_loading_shared_config(arg_value_provider: ArgumentValueFromConfigProvider):
    val = arg_value_provider.load_value(
        command_name="not_configured", argument_name="arg"
    )

    assert val == "a"


@pytest.mark.parametrize("configuration_profile_name", ["testnet"])
def test_loading_shared_profiled_config(
    arg_value_provider: ArgumentValueFromConfigProvider,
):
    val = arg_value_provider.load_value(
        command_name="not_configured", argument_name="arg"
    )

    assert val == "b"


@pytest.mark.parametrize("configuration_profile_name", [None])
def test_loading_command_config(arg_value_provider: ArgumentValueFromConfigProvider):
    val = arg_value_provider.load_value(command_name="deploy", argument_name="arg")

    assert val == "c"


@pytest.mark.parametrize("configuration_profile_name", ["testnet"])
def test_loading_command_profiled_config(
    arg_value_provider: ArgumentValueFromConfigProvider,
):
    val = arg_value_provider.load_value(command_name="deploy", argument_name="arg")

    assert val == "d"
