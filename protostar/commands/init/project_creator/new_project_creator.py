import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.configuration_file import (
    ConfigurationFileV2ContentFactory,
    ConfigurationFileV2Model,
)
from protostar.io import InputRequester
from protostar.protostar_exception import ProtostarException
from protostar.self import ProtostarVersion
from protostar.cairo import CairoVersion


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

    def run(self, cairo_version: CairoVersion, project_name: Optional[str] = None):
        project_config = (
            self.NewProjectConfig(project_name)
            if project_name
            else self._gather_input()
        )

        if cairo_version == CairoVersion.cairo1:
            self._validate_project_name(project_config.project_dirname)

        self._create_project(
            project_config=project_config,
            cairo_version=cairo_version,
        )

    def _gather_input(self) -> "NewProjectCreator.NewProjectConfig":
        project_dirname = self._requester.request_input("project directory name")
        while project_dirname == "":
            project_dirname = self._requester.request_input_again(
                "Please provide a non-empty project directory name"
            )

        return NewProjectCreator.NewProjectConfig(project_dirname)

    def _create_project(
        self,
        project_config: "NewProjectCreator.NewProjectConfig",
        cairo_version: CairoVersion,
    ) -> None:
        project_root_path = self._output_dir_path / project_config.project_dirname

        self._create_project_directory_from_template(
            cairo_version=cairo_version,
            project_root_path=project_root_path,
        )
        self._write_protostar_toml_from_config(
            project_root_path=project_root_path,
            configuration_model=self._new_project_config(cairo_version=cairo_version),
        )

    def _create_project_directory_from_template(
        self, cairo_version: CairoVersion, project_root_path: Path
    ):
        template_path = self.script_root / "templates" / cairo_version.value

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            new_template_path = Path(temp_dir) / "template"

            shutil.copytree(template_path, new_template_path)

            try:
                shutil.copytree(new_template_path, project_root_path)
            except FileExistsError as ex_file_exists:
                raise ProtostarException(
                    f"Folder or file named {project_root_path.name} already exists. Choose different project name."
                ) from ex_file_exists

    def _new_project_config(
        self, cairo_version: CairoVersion
    ) -> ConfigurationFileV2Model:
        if cairo_version == CairoVersion.cairo0:
            return ConfigurationFileV2Model(
                protostar_version=str(self._protostar_version),
                contract_name_to_path_strs={"main": ["src/main.cairo"]},
                project_config={
                    "lib-path": "lib",
                },
            )

        return ConfigurationFileV2Model(
            protostar_version=str(self._protostar_version),
            contract_name_to_path_strs={"hello_starknet": ["hello_starknet"]},
            project_config={
                "lib-path": "lib",
                "linked-libraries": ["hello_starknet"],
            },
        )

    @staticmethod
    def _validate_project_name(name: str):
        pattern = r"^[a-zA-Z0-9][a-zA-Z0-9_]*$"
        if not re.match(pattern, name):
            raise ProtostarException(
                f"Provided project name {name} does not match regex {pattern}. Choose a different project name."
            )
