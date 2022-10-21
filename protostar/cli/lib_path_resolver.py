from logging import getLogger
from pathlib import Path
from typing import Optional

from protostar.configuration_file import ConfigurationFile

from .common_arguments import lib_path_arg


class LibPathResolver:
    """
    This class resolves a path to the library directory uniformly for `ConfigurationFileV1` and `ConfigurationFileV2`.
    The lib-path was always configured in the CFV1 whereas CFV2 expects lib-path to be a command specific argument.
    """

    def __init__(
        self,
        project_root_path: Path,
        configuration_file: ConfigurationFile,
        legacy_mode: bool,
    ):
        self._project_root_path = project_root_path
        self._configuration_file = configuration_file
        self._legacy_mode = legacy_mode

    def resolve(self, lib_path_provided_as_arg: Optional[Path]) -> Path:
        if self._legacy_mode:
            if lib_path_provided_as_arg:
                getLogger().warning(
                    "Argument %s is ignored. "
                    "Please migrate your configuration file if the command `migrate-configuration-file` is available.",
                    lib_path_arg.name,
                )
            return (
                self._configuration_file.get_lib_path()
                or self._project_root_path / "lib"
            )
        return self._project_root_path / (lib_path_provided_as_arg or "lib")
