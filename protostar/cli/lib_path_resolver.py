from pathlib import Path
from typing import Optional

from protostar.configuration_file import ConfigurationFile


class LibPathResolver:
    """
    This class resolves a path to the library directory uniformly for `ConfigurationFileV1` and `ConfigurationFileV2`.
    The lib-path was always configured in the CFV1 whereas CFV2 expects lib-path to be a command specific argument.
    """

    def __init__(
        self,
        project_root_path: Path,
        configuration_file: ConfigurationFile,
        legacy_mode: bool = False,
    ):
        self._project_root_path = project_root_path
        self._configuration_file = configuration_file
        self._legacy_mode = legacy_mode

    def resolve(self, lib_path_provided_as_arg: Optional[Path]):
        if self._legacy_mode:
            return (
                self._configuration_file.get_lib_path()
                or self._project_root_path / "lib"
            )
        return self._project_root_path / (lib_path_provided_as_arg or "lib")
