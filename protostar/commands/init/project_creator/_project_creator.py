import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from typing_extensions import Literal

from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.protostar_toml.protostar_config_section import ProtostarConfigSection
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.self.protostar_directory import VersionManager


class ProjectCreator(ABC):
    def __init__(
        self,
        script_root: Path,
        protostar_toml_writer: ProtostarTOMLWriter,
        version_manager: VersionManager,
    ):
        self.script_root = script_root
        self.protostar_toml_writer = protostar_toml_writer
        self.version_manager = version_manager

    def copy_template(self, template_name: Literal["default"], project_root_path: Path):
        template_path = self.script_root / "templates" / template_name
        shutil.copytree(template_path, project_root_path)

    def save_protostar_toml(self, project_root: Path) -> None:
        self.protostar_toml_writer.save(
            path=project_root / "protostar.toml",
            protostar_config=ProtostarConfigSection.get_default(self.version_manager),
            protostar_project=ProtostarProjectSection(
                libs_relative_path=Path(self.default_lib_dirname),
            ),
            protostar_contracts=ProtostarContractsSection.get_default(),
        )

    @property
    def default_lib_dirname(self) -> str:
        return "lib"

    @abstractmethod
    def run(self) -> None:
        ...
