from pathlib import Path

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.git import Git


class AdaptedProjectCreator(ProjectCreator):
    def run(self):
        project_root_path = Path()
        self.save_protostar_toml(project_root_path=project_root_path)
        Git.init(project_root_path)
