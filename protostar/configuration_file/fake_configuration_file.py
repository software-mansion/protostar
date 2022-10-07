# pylint: disable=too-many-instance-attributes
from pathlib import Path
from typing import Any, Optional

from protostar.self import ProtostarVersion

from .configuration_file import ConfigurationFile, ConfigurationFileModelT


class FakeConfigurationFile(ConfigurationFile[ConfigurationFileModelT]):
    """
    This class can be used in tests and as a null object.
    https://en.wikipedia.org/wiki/Null_object_pattern
    """

    def __init__(
        self,
        file_path: Optional[Path] = None,
        declared_protostar_version: Optional[ProtostarVersion] = None,
        lib_path: Optional[Path] = None,
        contract_names: Optional[list[str]] = None,
        contract_source_paths: Optional[list[Path]] = None,
        read_model: Optional[ConfigurationFileModelT] = None,
        argument_value: Optional[Any] = None,
        shared_argument_value: Optional[Any] = None,
    ) -> None:
        super().__init__(profile_name="_")
        self._file_path = file_path
        self._declared_protostar_version = declared_protostar_version
        self._lib_path = lib_path
        self._contract_names = contract_names
        self._contract_source_paths = contract_source_paths
        self._read_model = read_model
        self._argument_value = argument_value
        self._shared_argument_value = shared_argument_value

    def get_filepath(self) -> Path:
        return self._file_path or Path() / "protostar.toml"

    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        return self._declared_protostar_version

    def get_lib_path(self) -> Optional[Path]:
        return self._lib_path

    def get_contract_names(self) -> list[str]:
        return self._contract_names or []

    def get_contract_source_paths(self, contract_name: str) -> list[Path]:
        return self._contract_source_paths or []

    def get_argument_value(
        self, command_name: str, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        return self._argument_value

    def get_shared_argument_value(
        self, argument_name: str, profile_name: Optional[str] = None
    ) -> Optional[Any]:
        return self._shared_argument_value

    def read(self) -> ConfigurationFileModelT:
        assert self._read_model is not None
        return self._read_model
