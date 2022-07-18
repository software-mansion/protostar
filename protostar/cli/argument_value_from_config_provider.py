from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader

SHARED_COMMAND_CONFIGS_SECTION_NAME = "shared_command_configs"


class ArgumentValueFromConfigProvider:
    def __init__(
        self,
        protostar_toml_reader: "ProtostarTOMLReader",
        configuration_profile_name: Optional[str] = None,
    ) -> None:
        self._protostar_toml_reader = protostar_toml_reader
        self._configuration_profile_name = configuration_profile_name
        super().__init__()

    def load_value(
        self, command_name: Optional[str], argument_name: str
    ) -> Optional[Any]:
        if self._configuration_profile_name and command_name:
            profile_cmd_arg = self._protostar_toml_reader.get_attribute(
                section_name=command_name,
                attribute_name=argument_name,
                profile_name=self._configuration_profile_name,
            )
            if profile_cmd_arg:
                return profile_cmd_arg

        if command_name:
            cmd_arg = self._protostar_toml_reader.get_attribute(
                section_name=command_name, attribute_name=argument_name
            )
            if cmd_arg:
                return cmd_arg

        if self._configuration_profile_name:
            profile_shared_arg = self._protostar_toml_reader.get_attribute(
                section_name=SHARED_COMMAND_CONFIGS_SECTION_NAME,
                attribute_name=argument_name,
                profile_name=self._configuration_profile_name,
            )
            if profile_shared_arg:
                return profile_shared_arg

        shared_arg = self._protostar_toml_reader.get_attribute(
            section_name=SHARED_COMMAND_CONFIGS_SECTION_NAME,
            attribute_name=argument_name,
        )
        return shared_arg
