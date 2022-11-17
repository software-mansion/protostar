import os
from logging import getLogger
from pathlib import Path

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
        self, relative_cairo_path_list: list[Path]
    ) -> list[Path]:
        cairo_paths = [
            *relative_cairo_path_list,
            self._project_root_path,
            *self._build_libs_cairo_path_list(),
        ]
        self._warn_if_path_does_not_exist(cairo_paths)
        return cairo_paths

    def _warn_if_path_does_not_exist(self, cairo_paths: list[Path]):
        for cairo_path in cairo_paths:
            if not cairo_path.exists():
                getLogger().warning(
                    "The following Cairo Path directory doesn't exist: %s", cairo_path
                )

    def _build_libs_cairo_path_list(self) -> list[Path]:
        libs_path = self._configuration_file.get_lib_path()
        if libs_path is None:
            return []
        return [libs_path, *self._build_packages_cairo_path_list()]

    def _build_packages_cairo_path_list(self) -> list[Path]:
        libs_path = self._configuration_file.get_lib_path()
        if libs_path is None or not libs_path.exists():
            return []
        assert libs_path.is_dir(), f"{libs_path} is not a directory"
        (root, dirs, _) = next(os.walk(str(libs_path.resolve())))
        return [Path(root, directory).resolve() for directory in dirs]
