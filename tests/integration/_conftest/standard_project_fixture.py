from pathlib import Path
from unittest.mock import MagicMock

import pytest

from protostar.commands.init.project_creator import ProjectCreator
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.utils.protostar_directory import VersionManager


class SimpleProjectCreator(ProjectCreator):
    def __init__(
        self,
        project_root_path: Path,
        script_root: Path,
        protostar_toml_writer: ProtostarTOMLWriter,
        version_manager: VersionManager,
    ):
        super().__init__(
            script_root,
            protostar_toml_writer,
            version_manager,
        )
        self._project_root_path = project_root_path

    def run(self):
        self.copy_template("default", self._project_root_path)
        self.save_protostar_toml(self._project_root_path, Path("./lib"))
        self._create_libs_dir()

    def _create_libs_dir(self) -> None:
        (self._project_root_path / "lib").mkdir(exist_ok=True, parents=True)


@pytest.fixture(name="project_root_path")
def project_root_path_fixture(tmp_path: Path) -> Path:
    return tmp_path / "default_project"


@pytest.fixture(name="version_manager")
def version_manager_fixture(mocker: MagicMock) -> VersionManager:
    version_manager = mocker.MagicMock()
    version_manager.protostar_version = mocker.MagicMock()
    version_manager.protostar_version = "99.9.9"
    return version_manager


STANDARD_PROJECT_FIXTURE = "standard_project"


@pytest.fixture(name=STANDARD_PROJECT_FIXTURE)
def standard_project_fixture(project_root_path: Path, version_manager: VersionManager):
    protostar_toml_writer = ProtostarTOMLWriter()
    project_creator = SimpleProjectCreator(
        project_root_path=project_root_path,
        protostar_toml_writer=protostar_toml_writer,
        script_root=Path(__file__).parent / ".." / ".." / "..",
        version_manager=version_manager,
    )
    project_creator.run()
