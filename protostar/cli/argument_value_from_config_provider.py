from typing import Any, Optional

from protostar.utils import Project


class ArgumentValueFromConfigProvider:
    def __init__(
        self, project: Project, configuration_profile_name: Optional[str] = None
    ) -> None:
        self._project = project
        self._configuration_profile_name = configuration_profile_name
        super().__init__()

    def load_value(
        self, command_name: Optional[str], argument_name: str
    ) -> Optional[Any]:
        if self._configuration_profile_name and command_name:
            profile_cmd_arg = self._project.load_argument(
                command_name, argument_name, self._configuration_profile_name
            )
            if profile_cmd_arg:
                return profile_cmd_arg

        if command_name:
            cmd_arg = self._project.load_argument(command_name, argument_name)
            if cmd_arg:
                return cmd_arg

        if self._configuration_profile_name:
            profile_shared_arg = self._project.load_argument(
                self._project.shared_command_configs_section_name,
                argument_name,
                self._configuration_profile_name,
            )
            if profile_shared_arg:
                return profile_shared_arg

        shared_arg = self._project.load_argument(
            self._project.shared_command_configs_section_name, argument_name
        )
        return shared_arg
