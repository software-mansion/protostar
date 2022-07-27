from pathlib import Path
from typing import Optional

import pytest

from protostar.cli.argument_value_from_config_provider import (
    ArgumentValueFromConfigProvider,
)
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader


@pytest.fixture(name="configuration_profile_name")
def configuration_profile_name_fixture() -> Optional[str]:
    return None


@pytest.fixture(name="arg_value_provider")
def arg_value_provider_fixture(datadir: Path, configuration_profile_name):
    return ArgumentValueFromConfigProvider(
        protostar_toml_reader=ProtostarTOMLReader(
            protostar_toml_path=datadir / "protostar.toml"
        ),
        configuration_profile_name=configuration_profile_name,
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


@pytest.mark.parametrize("configuration_profile_name", [None])
def test_returning_none_when_file_config_file_does_not_exists(
    arg_value_provider: ArgumentValueFromConfigProvider,
):
    # pylint: disable=protected-access
    arg_value_provider._protostar_toml_reader.path = Path() / "NOT_EXISTING_DIR"

    val = arg_value_provider.load_value(command_name="deploy", argument_name="arg")

    assert val is None
