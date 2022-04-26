from typing import Any, Optional

from src.core.argument_parser_facade import ArgumentDefaultValueProvider
from src.core.command import Command
from src.utils import Project


class ArgumentDefaultValueFromConfigProvider(ArgumentDefaultValueProvider):
    def __init__(self, project: Project) -> None:
        self._project = project
        super().__init__()

    def get_default_value(
        self, command: Optional[Command], argument: Command.Argument
    ) -> Optional[Any]:
        shared_config = self._project.load_argument(
            "shared_command_configs", argument.name
        )

        command_name = command.name if command else "shared_command_configs"
        command_scope_config = self._project.load_argument(command_name, argument.name)
        return command_scope_config or shared_config
