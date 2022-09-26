import pytest

from protostar.configuration_file import CommandNamesProvider

from .command_names_delayed_provider import CommandNamesDelayedProvider


class CommandNamesProviderDouble(CommandNamesProvider):
    def get_command_names(self) -> list[str]:
        return ["foo", "bar"]


def test_retrieving_command_names():
    command_names_aggregator = CommandNamesDelayedProvider()
    command_names_aggregator.set_command_names_provider(CommandNamesProviderDouble())

    result = command_names_aggregator.get_command_names()

    assert result == ["foo", "bar"]


def test_retrieving_command_names_failure_when_actual_provider_is_not_set():
    command_names_aggregator = CommandNamesDelayedProvider()

    with pytest.raises(AssertionError):
        command_names_aggregator.get_command_names()
