import os
from pathlib import Path
from typing import List

from protostar.configuration_file import ConfigurationFile


class ProjectCairoPathBuilder:
    def __init__(
        self,
        project_root_path: Path,
        configuration_file: ConfigurationFile,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._configuration_file = configuration_file

    def build_project_cairo_path_list(
        self, relative_cairo_path_list: List[Path]
    ) -> List[Path]:
        """NOTE: This function uses `list` suffix to mitigate confusion and
        remain consistency with StarkNet's `cairo_path`."""

        return [
            *relative_cairo_path_list,
            self._project_root_path,
            *self._build_libs_cairo_path_list(),
        ]

    def _build_libs_cairo_path_list(self) -> List[Path]:
        libs_path = self._configuration_file.get_lib_path()
        if libs_path is None:
            return []
        return [libs_path, *self._build_packages_cairo_path_list()]

    def _build_packages_cairo_path_list(self) -> List[Path]:
        libs_path = self._configuration_file.get_lib_path()
        if libs_path is None:
            return []
        (root, dirs, _) = next(os.walk(str(libs_path.resolve())))
        return [Path(root, directory).resolve() for directory in dirs]
