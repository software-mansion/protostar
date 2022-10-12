from abc import ABC, abstractmethod
from typing import Any, Optional

from protostar.cli import ConfigFileArgumentResolverProtocol


class ArgumentValueResolver(ABC, ConfigFileArgumentResolverProtocol):
    def __init__(self, profile_name: Optional[str]) -> None:
        self._profile_name = profile_name

    def resolve_argument(
        self, command_name: Optional[str], argument_name: str
    ) -> Optional[Any]:
        if self._profile_name and command_name:
            profile_cmd_arg = self.get_argument_value(
                command_name=command_name,
                argument_name=argument_name,
                profile_name=self._profile_name,
            )
            if profile_cmd_arg:
                return profile_cmd_arg

        if command_name:
            cmd_arg = self.get_argument_value(
                argument_name=argument_name,
                command_name=command_name,
                profile_name=self._profile_name,
            )
            if cmd_arg:
                return cmd_arg

        if self._profile_name:
            profile_shared_arg = self.get_shared_argument_value(
                argument_name=argument_name,
                profile_name=self._profile_name,
            )
            if profile_shared_arg:
                return profile_shared_arg

        shared_arg = self.get_shared_argument_value(
            argument_name=argument_name,
            profile_name=self._profile_name,
        )
        return shared_arg

    @abstractmethod
    def get_argument_value(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        ...

    @abstractmethod
    def get_shared_argument_value(
        self, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        ...
