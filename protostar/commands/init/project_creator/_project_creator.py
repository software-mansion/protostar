import shutil
from abc import ABC
from pathlib import Path

from protostar.configuration_file import (
    ConfigurationFileV2ContentFactory,
    ConfigurationFileV2Model,
)
from protostar.self import ProtostarVersion
from protostar.cairo import CairoVersion


class ProjectCreator(ABC):
    def __init__(
        self,
        script_root: Path,
        configuration_file_content_factory: ConfigurationFileV2ContentFactory,
        protostar_version: ProtostarVersion,
    ):
        self.script_root = script_root
        self._configuration_file_content_factory = configuration_file_content_factory
        self._protostar_version = protostar_version

    def copy_template(self, cairo_version: CairoVersion, project_root_path: Path):
        template_path = self.script_root / "templates" / cairo_version.value
        shutil.copytree(template_path, project_root_path)

    def save_protostar_toml(self, project_root_path: Path) -> None:
        configuration_file_content = (
            self._configuration_file_content_factory.create_file_content(
                ConfigurationFileV2Model(
                    protostar_version=str(self._protostar_version),
                    contract_name_to_path_strs={"main": ["src/main.cairo"]},
                    project_config={"lib-path": "lib"},
                    command_name_to_config={},
                    profile_name_to_project_config={},
                    profile_name_to_commands_config={},
                )
            )
        )
        ext = self._configuration_file_content_factory.get_file_extension()
        Path(project_root_path / f"protostar.{ext}").write_text(
            configuration_file_content, encoding="utf-8"
        )
