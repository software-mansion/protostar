from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.utils import InputRequester
from protostar.utils.protostar_directory import VersionManager
from protostar.git.git_repository import GitRepository


class NewProjectCreator(ProjectCreator):
    @dataclass
    class UserInput:
        project_dirname: str
        lib_dirname: str

    def __init__(
        self,
        script_root: Path,
        requester: InputRequester,
        protostar_toml_writer: ProtostarTOMLWriter,
        version_manager: VersionManager,
        output_dir_path: Optional[Path] = None,
    ):
        super().__init__(script_root, protostar_toml_writer, version_manager)
        self._protostar_toml_writer = protostar_toml_writer
        self._version_manager = version_manager
        self._requester = requester
        self._output_dir_path = output_dir_path or Path()

    def run(self):
        self._create_project(self._gather_input())

    def _gather_input(self) -> "NewProjectCreator.UserInput":

        project_dirname = self._requester.request_input("project directory name")
        while project_dirname == "":
            project_dirname = self._requester.request_input_again(
                "Please provide a non-empty project directory name"
            )

        lib_dirname = (
            self._requester.request_input("libraries directory name (lib)") or "lib"
        )

        return NewProjectCreator.UserInput(project_dirname, lib_dirname)

    def _create_project(self, user_input: "NewProjectCreator.UserInput") -> None:
        output_dir_path = self._output_dir_path
        project_root_path = output_dir_path / user_input.project_dirname
        self.copy_template("default", project_root_path)

        libs_path = Path(project_root_path, user_input.lib_dirname)

        if not libs_path.is_dir():
            libs_path.mkdir(parents=True)

        self.save_protostar_toml(
            project_root_path, libs_path=Path(user_input.lib_dirname)
        )

        repo = GitRepository(project_root_path)
        if not repo.is_initialized():
            repo.init()
