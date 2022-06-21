from pathlib import Path

from git import InvalidGitRepositoryError
from git.repo import Repo

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.utils import InputRequester
from protostar.utils.protostar_directory import VersionManager


class NewProjectCreator(ProjectCreator):
    class UserInput:
        project_dirname: str
        lib_dirname: str

    def __init__(
        self,
        script_root: Path,
        requester: InputRequester,
        protostar_toml_writer: ProtostarTOMLWriter,
        version_manager: VersionManager,
    ):
        super().__init__(script_root, protostar_toml_writer, version_manager)
        self._protostar_toml_writer = protostar_toml_writer
        self._version_manager = version_manager
        self._requester = requester

    def run(self):
        self._create_project(self._gather_input())

    def _gather_input(self) -> "NewProjectCreator.UserInput":
        user_input = NewProjectCreator.UserInput()

        user_input.project_dirname = self._requester.request_input(
            "project directory name"
        )
        while user_input.project_dirname == "":
            user_input.project_dirname = self._requester.request_input_again(
                "Please provide a non-empty project directory name"
            )

        user_input.lib_dirname = (
            self._requester.request_input("libraries directory name (lib)") or "lib"
        )

        return user_input

    def _create_project(self, user_input: "NewProjectCreator.UserInput") -> None:
        project_root_path = Path() / user_input.project_dirname
        self.copy_template("default", project_root_path)

        libs_path = Path(project_root_path, user_input.lib_dirname)

        if not libs_path.is_dir():
            libs_path.mkdir(parents=True)

        self.save_protostar_toml(
            project_root_path, libs_path=Path(user_input.lib_dirname)
        )

        try:
            Repo(project_root_path, search_parent_directories=True)
        except InvalidGitRepositoryError:
            Repo.init(project_root_path)
