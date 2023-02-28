from pathlib import Path

class ProjectCairoPathBuilder:
    def __init__(
        self,
        project_root_path: Path,
    ) -> None:
        super().__init__()
        self._project_root_path = project_root_path
    def build_project_cairo_path_list(
        self, relative_cairo_path_list: list[Path], include_root: bool = True 
    ) -> list[Path]:
        root: list[Path] = ([self._project_root_path] if include_root else [])
        return [
            *relative_cairo_path_list,
        ] + root
