from .configuration_file_v1 import CommandNamesProviderProtocol
from .fake_configuration_file import FakeConfigurationFile

PROTOSTAR_TOML_V1_CONTENT = """
["protostar.config"]
protostar_version = "0.4.0"
"""

PROTOSTAR_TOML_V2_CONTENT = """
[project]
protostar-version = "0.5.0"
"""


class FakeCommandNamesProvider(CommandNamesProviderProtocol):
    def __init__(self, command_names: list[str]) -> None:
        super().__init__()
        self._command_names = command_names

    def get_command_names(self) -> list[str]:
        return self._command_names
