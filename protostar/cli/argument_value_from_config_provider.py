from typing import Any, Optional

from protostar.cli.command import Command
from protostar.utils import Project


class ArgumentValueFromConfigProvider:
    def __init__(
        self, project: Project, configuration_profile_name: Optional[str] = None
    ) -> None:
        self._project = project
        self._configuration_profile_name = configuration_profile_name
        super().__init__()

    def get_default_value(
        self, command: Optional[Command], argument: Command.Argument
    ) -> Optional[Any]:
        if self._configuration_profile_name and command:
            profile_cmd_arg = self._project.load_argument(
                f"{command.name}.{self._configuration_profile_name}", argument.name
            )
            if profile_cmd_arg:
                return profile_cmd_arg

        if command:
            cmd_arg = self._project.load_argument(command.name, argument.name)
            if cmd_arg:
                return cmd_arg

        if self._configuration_profile_name:
            profile_shared_arg = self._project.load_argument(
                f"{self._project.shared_command_configs_section_name}.{self._configuration_profile_name}",
                argument.name,
            )
            if profile_shared_arg:
                return profile_shared_arg

        shared_arg = self._project.load_argument(
            self._project.shared_command_configs_section_name, argument.name
        )
        return shared_arg
