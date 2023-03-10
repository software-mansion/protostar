from pathlib import Path

from protostar.cairo import CairoVersion
from protostar.commands.init.project_creator._project_creator import ProjectCreator


class AdaptedProjectCreator(ProjectCreator):
    def run(self, cairo_version: CairoVersion):
        project_root_path = Path()
        self.save_protostar_toml(
            project_root_path=project_root_path, cairo_version=cairo_version
        )
