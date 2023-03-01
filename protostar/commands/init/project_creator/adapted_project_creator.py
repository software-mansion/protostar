from pathlib import Path

from protostar.commands.init.project_creator._project_creator import ProjectCreator


class AdaptedProjectCreator(ProjectCreator):
    def run(self, is_cairo_1: bool):
        project_root_path = Path()
        self.save_protostar_toml(project_root_path=project_root_path)
