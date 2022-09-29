from typing import Any, Optional, Protocol


class ArgumentValueProviderProtocol(Protocol):
    def get_argument_value(
        self, command_name: str, argument_name: str, profile_name: Optional[str]
    ) -> Optional[Any]:
        ...

    def get_shared_argument_value(
        self, argument_name: str, profile_name: Optional[str]
    ) -> Optional[Any]:
        ...


class ArgumentValueFromConfigProvider:
    def __init__(
        self,
        argument_value_provider: ArgumentValueProviderProtocol,
        configuration_profile_name: Optional[str] = None,
    ) -> None:
        self._argument_value_provider = argument_value_provider
        self._configuration_profile_name = configuration_profile_name
        super().__init__()

    def load_value(
        self, command_name: Optional[str], argument_name: str
    ) -> Optional[Any]:
        if self._configuration_profile_name and command_name:
            profile_cmd_arg = self._argument_value_provider.get_argument_value(
                command_name=command_name,
                argument_name=argument_name,
                profile_name=self._configuration_profile_name,
            )
            if profile_cmd_arg:
                return profile_cmd_arg

        if command_name:
            cmd_arg = self._argument_value_provider.get_argument_value(
                argument_name=argument_name,
                command_name=command_name,
                profile_name=self._configuration_profile_name,
            )
            if cmd_arg:
                return cmd_arg

        if self._configuration_profile_name:
            profile_shared_arg = (
                self._argument_value_provider.get_shared_argument_value(
                    argument_name=argument_name,
                    profile_name=self._configuration_profile_name,
                )
            )
            if profile_shared_arg:
                return profile_shared_arg

        shared_arg = self._argument_value_provider.get_shared_argument_value(
            argument_name=argument_name,
            profile_name=self._configuration_profile_name,
        )
        return shared_arg
