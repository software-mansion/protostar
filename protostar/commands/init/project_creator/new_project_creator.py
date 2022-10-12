from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.io import InputRequester
from protostar.self.protostar_directory import VersionManager
from protostar.git import Git


class NewProjectCreator(ProjectCreator):
    @dataclass
    class NewProjectConfig:
        project_dirname: str

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

    def run(self, project_name: Optional[str] = None):
        project_config = (
            NewProjectCreator.NewProjectConfig(project_name)
            if project_name
            else self._gather_input()
        )

        self._create_project(project_config)

    def _gather_input(self) -> "NewProjectCreator.NewProjectConfig":
        project_dirname = self._requester.request_input("project directory name")
        while project_dirname == "":
            project_dirname = self._requester.request_input_again(
                "Please provide a non-empty project directory name"
            )

        return NewProjectCreator.NewProjectConfig(project_dirname)

    def _create_project(self, user_input: "NewProjectCreator.NewProjectConfig") -> None:
        output_dir_path = self._output_dir_path
        project_root_path = output_dir_path / user_input.project_dirname
        self.copy_template("default", project_root_path)

        libs_path = project_root_path / self.default_lib_dirname

        if not libs_path.is_dir():
            libs_path.mkdir(parents=True)

        self.save_protostar_toml(project_root=project_root_path)

        Git.init(project_root_path)
