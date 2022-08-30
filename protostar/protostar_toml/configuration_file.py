from typing import Optional

from typing_extensions import Protocol

from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils.protostar_directory import VersionManager, VersionType


class ConfigurationFile(Protocol):
    def get_min_protostar_version(self) -> VersionType:
        ...


class ConfigurationFileV1(ConfigurationFile):
    def __init__(self, protostar_toml_reader: ProtostarTOMLReader) -> None:
        super().__init__()
        self._protostar_toml_reader = protostar_toml_reader

    def get_min_protostar_version(self) -> Optional[VersionType]:
        version_str = self._protostar_toml_reader.get_attribute(
            attribute_name="protostar_version", section_name="config"
        )
        if not version_str:
            return None
        return VersionManager.parse(version_str)
