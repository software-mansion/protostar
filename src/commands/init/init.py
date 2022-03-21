import shutil
from pathlib import Path
import stat
from typing import Any

from colorama import Fore
from git.repo import Repo

from src.utils import log_color_provider
from src.utils.config.project import Project, ProjectConfig


def init(args: Any, script_root: str):
    """
    Creates init protostar project
    """
    if args.only_config:
        project_creator = OnlyConfigCreator(script_root)
    else:
        project_creator = ProjectCreator(script_root)
    
    project_creator.create()


class ProjectCreator:

    def __init__(self, script_root: str):
        self.script_root = script_root

    @staticmethod
    def request_input(message: str):
        return input(
            f"{log_color_provider.get_color('CYAN')}{message}:{log_color_provider.get_color('RESET')} "
        )

    def create(self):
        self.interactive_input()
        self.project_creation()


    def interactive_input(self) -> ProjectConfig:
        project_name = ProjectCreator.request_input("Project name: ")
        project_description = ProjectCreator.request_input("Project description")
        author = ProjectCreator.request_input("Author")
        version = ProjectCreator.request_input("Version")
        project_license = ProjectCreator.request_input("License")
        lib_dir = ProjectCreator.request_input("Libraries directory name (optional)")
        self.config = ProjectConfig(
            name=project_name,
            description=project_description,
            license=project_license,
            version=version,
            authors=[author],
            libs_path=lib_dir
        )

    def project_creation(self):
        project_root = Path() / self.config.name
        self.copy_template(self.script_root, "default", project_root)
        project = Project(project_root=project_root)

        lib_pth = Path(project_root, self.config.libs_path)

        if self.config.libs_path and not lib_pth.is_dir():
            lib_pth.mkdir(parents=True)

        project.write_config(self.config)

        Repo.init(project_root)

    def copy_template(self, script_root: str, template_name: str, project_path: Path):
        template_path = f"{script_root}/templates/{template_name}"
        shutil.copytree(template_path, project_path)


class OnlyConfigCreator(ProjectCreator):
    def project_creation(self):
        project_root = Path()

        lib_pth = Path(project_root, self.config.libs_path)

        if self.config.libs_path and not lib_pth.is_dir():
            lib_pth.mkdir(parents=True)

        project = Project(project_root=project_root)
        project.write_config(self.config)

