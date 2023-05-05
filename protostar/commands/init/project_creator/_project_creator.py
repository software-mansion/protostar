import shutil
from abc import ABC
from pathlib import Path

from protostar.configuration_file import (
    ConfigurationFileV2ContentFactory,
    ConfigurationFileV2Model,
)
from protostar.protostar_exception import ProtostarException
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
        try:
            shutil.copytree(template_path, project_root_path)
        except FileExistsError as ex_file_exists:
            raise ProtostarException(
                f"Folder or file named {project_root_path.name} already exists. Choose different project name."
            ) from ex_file_exists

    def _write_protostar_toml_from_config(
        self, project_root_path: Path, configuration_model: ConfigurationFileV2Model
    ) -> None:
        configuration_file_content = (
            self._configuration_file_content_factory.create_file_content(
                configuration_model
            )
        )
        ext = self._configuration_file_content_factory.get_file_extension()
        Path(project_root_path / f"protostar.{ext}").write_text(
            configuration_file_content, encoding="utf-8"
        )
