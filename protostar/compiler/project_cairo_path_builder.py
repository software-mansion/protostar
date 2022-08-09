import os
from pathlib import Path
from typing import List, Optional

from typing_extensions import Protocol

from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection


class ProjectCairoPathBuilder:
    def __init__(
        self,
        project_root_path: Path,
        project_section_loader: ProtostarProjectSection.Loader,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
        self._project_section_loader = project_section_loader

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
        libs_path = self._get_libs_path()
        if libs_path is None:
            return []
        return [libs_path, *self._build_packages_cairo_path_list()]

    def _build_packages_cairo_path_list(self) -> List[Path]:
        libs_path = self._get_libs_path()
        if libs_path is None:
            return []
        (root, dirs, _) = next(os.walk(str(libs_path.resolve())))
        return [Path(root, directory).resolve() for directory in dirs]

    def _get_libs_path(self) -> Optional[Path]:
        project_section = self._project_section_loader.load()
        return project_section.get_libs_path(self._project_root_path)
