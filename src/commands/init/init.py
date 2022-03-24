import glob
import shutil
from pathlib import Path
from typing import Any, Type

from git.repo import Repo


from src.utils import log_color_provider
from src.utils.config.project import Project, ProjectConfig


def init(args: Any, script_root: str):
    """
    Creates init protostar project
    """
    project_creator = get_creator(args)
    project_creator = project_creator(script_root)
    project_creator.create()


def input_yes_no(message: str) -> bool:
    res = ProjectCreator.request_input(message + " [y/n]")
    while res not in ("y", "n"):
        res = ProjectCreator.request_input("Please provide one of the [y/n]")
    return res == "y"


class ProjectCreator:
    def __init__(self, script_root: str):
        self.script_root = script_root
        self.config = ProjectConfig()

    @staticmethod
    def request_input(message: str):
        return input(
            f"{log_color_provider.get_color('CYAN')}{message}:{log_color_provider.get_color('RESET')} "
        )

    @staticmethod
    def request_input_warning(message: str):
        return input(
            f"{log_color_provider.get_color('RED')}{message}:{log_color_provider.get_color('RESET')} "
        )

    def create(self):
        self.interactive_input()
        self.project_creation()

    def interactive_input(self):
        project_name = ProjectCreator.request_input("Project name")
        while project_name == "":
            project_name = ProjectCreator.request_input_warning(
                "Please provide a non-empty project name"
            )
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
            libs_path=lib_dir,
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

    @staticmethod
    def copy_template(script_root: str, template_name: str, project_path: Path):
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


def get_creator(args: Any) -> Type[ProjectCreator]:
    if args.existing:
        return OnlyConfigCreator

    files_depth_3 = glob.glob("*/*/*")
    is_any_cairo_file = any(map(lambda f: f.endswith(".cairo"), files_depth_3))

    out = False
    if is_any_cairo_file:
        out = input_yes_no(
            "There are cairo files in your working directory.\n"
            "Do you want to adapt current working directory "
            "as a project instead of creating a new project?."
        )

    return OnlyConfigCreator if out else ProjectCreator
