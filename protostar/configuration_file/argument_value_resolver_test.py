from typing import Any, Optional

import pytest

from .argument_value_resolver import ArgumentValueResolver


class FakeArgumentValueProvider(ArgumentValueResolver):
    def __init__(
        self, profile_name: Optional[str], ignore_command_scoped_value: bool
    ) -> None:
        super().__init__(profile_name)
        self._ignore_command_scoped_value = ignore_command_scoped_value

    def get_argument_value(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        if self._ignore_command_scoped_value:
            return None
        profile_name_prefix = f"{profile_name}::" if profile_name else ""
        return f"{profile_name_prefix}{command_name}::{argument_name}"

    def get_shared_argument_value(
        self, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        profile_name_prefix = f"{profile_name}::" if profile_name else ""
        return f"{profile_name_prefix}shared::{argument_name}"


@pytest.fixture(name="arg_value_provider")
def arg_value_provider_fixture(
    configuration_profile_name: Optional[str],
    ignore_command_scoped_value: bool,
):
    return FakeArgumentValueProvider(
        profile_name=configuration_profile_name,
        ignore_command_scoped_value=ignore_command_scoped_value,
    )


@pytest.mark.parametrize(
    "configuration_profile_name, ignore_command_scoped_value", ((None, True),)
)
def test_loading_shared_config(arg_value_provider: ArgumentValueResolver):
    val = arg_value_provider.resolve_argument(
        command_name="command", argument_name="arg"
    )

    assert val == "shared::arg"


@pytest.mark.parametrize(
    "configuration_profile_name, ignore_command_scoped_value", (("profile", True),)
)
def test_loading_shared_profiled_config(
    arg_value_provider: ArgumentValueResolver,
):
    val = arg_value_provider.resolve_argument(
        command_name="command", argument_name="arg"
    )

    assert val == "profile::shared::arg"


@pytest.mark.parametrize(
    "configuration_profile_name, ignore_command_scoped_value", ((None, False),)
)
def test_loading_command_config(arg_value_provider: ArgumentValueResolver):
    val = arg_value_provider.resolve_argument(
        command_name="command", argument_name="arg"
    )

    assert val == "command::arg"


@pytest.mark.parametrize(
    "configuration_profile_name, ignore_command_scoped_value", (("profile", True),)
)
def test_loading_command_profiled_config(
    arg_value_provider: ArgumentValueResolver,
):
    val = arg_value_provider.resolve_argument(
        command_name="command", argument_name="arg"
    )

    assert val == "profile::shared::arg"
