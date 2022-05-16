import glob
import shutil
from pathlib import Path
from typing import Any, List, Optional, Type

from git.exc import InvalidGitRepositoryError
from git.repo import Repo

from protostar.cli import Command
from protostar.utils import VersionManager, log_color_provider
from protostar.utils.config.project import Project, ProjectConfig


class InitCommand(Command):
    def __init__(self, script_root: Path, version_manager: VersionManager) -> None:
        super().__init__()
        self._script_root = script_root
        self._version_manager = version_manager

    @property
    def name(self) -> str:
        return "init"

    @property
    def description(self) -> str:
        return "Create a Protostar project."

    @property
    def example(self) -> Optional[str]:
        return "$ protostar init"

    @property
    def arguments(self) -> List[Command.Argument]:
        return [
            Command.Argument(
                name="existing",
                description="Adapt current directory to a Protostar project.",
                type="bool",
            )
        ]

    async def run(self, args):
        init(args, self._script_root, self._version_manager)


def init(args: Any, script_root: Path, version_manager: VersionManager):
    """
    Creates init protostar project
    """
    CurrentProjectCreator = get_creator(args)
    project_creator = CurrentProjectCreator(script_root, version_manager)
    project_creator.run()


def input_yes_no(message: str) -> bool:
    res = ProjectCreator.request_input(message + " [y/n]")
    while res not in ("y", "n"):
        res = ProjectCreator.request_input("Please provide one of the [y/n]")
    return res == "y"


class ProjectCreator:
    def __init__(self, script_root: Path, version_manager: VersionManager):
        self.script_root = script_root
        self.config = ProjectConfig()
        self._version_manager = version_manager
        self._project_dir_name = ""

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

    def run(self):
        self.interactive_input()
        self.project_creation()

    def interactive_input(self):
        project_dir_name = ProjectCreator.request_input("project directory name")
        while project_dir_name == "":
            project_dir_name = ProjectCreator.request_input_warning(
                "Please provide a non-empty project directory name"
            )
        self._project_dir_name = project_dir_name
        lib_dir = (
            ProjectCreator.request_input("libraries directory name (lib)") or "lib"
        )
        self.config = ProjectConfig(
            libs_path=lib_dir,
        )

    def project_creation(self):
        project_root = Path() / self._project_dir_name
        self.copy_template(self.script_root, "default", project_root)
        project = Project(self._version_manager, project_root)

        lib_pth = Path(project_root, self.config.libs_path)

        if self.config.libs_path and not lib_pth.is_dir():
            lib_pth.mkdir(parents=True)

        project.write_config(self.config)

        try:
            Repo(project_root, search_parent_directories=True)
        except InvalidGitRepositoryError:
            Repo.init(project_root)

    @staticmethod
    def copy_template(script_root: Path, template_name: str, project_path: Path):
        template_path = script_root / "templates" / template_name
        shutil.copytree(template_path, project_path)


class OnlyConfigCreator(ProjectCreator):
    def interactive_input(self):
        self._project_dir_name = Path.cwd().name
        lib_dir = (
            ProjectCreator.request_input("libraries directory name (lib)") or "lib"
        )
        self.config = ProjectConfig(
            libs_path=lib_dir,
        )

    def project_creation(self):
        project_root = Path()

        lib_pth = Path(project_root, self.config.libs_path)

        if self.config.libs_path and not lib_pth.is_dir():
            lib_pth.mkdir(parents=True)

        project = Project(self._version_manager, project_root)
        project.write_config(self.config)

        try:
            Repo(project_root, search_parent_directories=True)
        except InvalidGitRepositoryError:
            Repo.init(project_root)


def get_creator(args: Any) -> Type[ProjectCreator]:
    if args.existing:
        return OnlyConfigCreator

    files_depth_3 = glob.glob("*") + glob.glob("*/*") + glob.glob("*/*/*")
    can_be_a_project = any(
        map(lambda f: f.endswith(".cairo") or f == ".git", files_depth_3)
    ) and "protostar.toml" not in glob.glob("*")

    out = False
    if can_be_a_project:
        out = input_yes_no(
            "Your current directory may be a cairo project.\n"
            "Do you want to adapt current working directory "
            "as a project instead of creating a new project?."
        )

    return OnlyConfigCreator if out else ProjectCreator
