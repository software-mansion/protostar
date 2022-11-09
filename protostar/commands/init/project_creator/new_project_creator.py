from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.configuration_file import ConfigurationFileV2ContentFactory
from protostar.git import Git
from protostar.io import InputRequester
from protostar.self import ProtostarVersion


class NewProjectCreator(ProjectCreator):
    @dataclass
    class NewProjectConfig:
        project_dirname: str

    def __init__(
        self,
        script_root: Path,
        requester: InputRequester,
        protostar_version: ProtostarVersion,
        configuration_file_content_factory: ConfigurationFileV2ContentFactory,
        output_dir_path: Optional[Path] = None,
    ):
        super().__init__(
            script_root,
            configuration_file_content_factory=configuration_file_content_factory,
            protostar_version=protostar_version,
        )
        self._protostar_version = protostar_version
        self._requester = requester
        self._output_dir_path = output_dir_path or Path()
        self._configuration_file_content_factory = configuration_file_content_factory

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
        self.save_protostar_toml(project_root_path=project_root_path)
        Git.init(project_root_path)
