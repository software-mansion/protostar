from pytest_mock import MockerFixture

from conftest import FooCommand
from src.cli.argument_value_from_config_provider import (
    ArgumentValueFromConfigProvider,
)
from src.utils import Project


def test_should_get_config(mocker: MockerFixture, foo_command: FooCommand):
    project = Project(mocker.MagicMock())
    project.load_argument = mocker.MagicMock()
    project.load_argument.return_value = "x"
    arg_provider = ArgumentValueFromConfigProvider(project)
    arg = foo_command.arguments[0]

    result = arg_provider.get_default_value(foo_command, arg)

    assert project.load_argument.call_args_list[0][0] == (
        "shared_command_configs",
        arg.name,
    ), "Get a shared config"
    assert project.load_argument.call_args_list[1][0] == (
        foo_command.name,
        arg.name,
    ), "Get a command config"
    assert result == "x"
