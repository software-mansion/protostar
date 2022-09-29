from typing import Optional

from .configuration_file_v1 import CommandNamesProviderProtocol


class CommandNamesDelayedProvider(CommandNamesProviderProtocol):
    def __init__(self) -> None:
        super().__init__()
        self._command_names_provider: Optional[CommandNamesProviderProtocol] = None

    def set_command_names_provider(
        self, command_names_provider: CommandNamesProviderProtocol
    ) -> None:
        self._command_names_provider = command_names_provider

    def get_command_names(self) -> list[str]:
        assert self._command_names_provider is not None
        return self._command_names_provider.get_command_names()
