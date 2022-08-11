from pathlib import Path

from pytest_mock import MockerFixture
from typing_extensions import Self

from protostar.commands.init.project_creator import ProjectCreator
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.compiler.project_compiler import ProjectCompilerConfig
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_toml import (
    ProtostarContractsSection,
    ProtostarProjectSection,
    ProtostarTOMLReader,
    ProtostarTOMLWriter,
)
from protostar.starknet_gateway import GatewayFacade
from protostar.utils import VersionManager


class ProtostarFixture:
    def __init__(
        self,
        simple_project_creator: "SimpleProjectCreator",
        project_compiler: ProjectCompiler,
        migrator_builder: Migrator.Builder,
    ) -> None:
        self._simple_project_creator = simple_project_creator
        self._project_compiler = project_compiler
        self._migrator_builder = migrator_builder

    async def init(self) -> Self:
        self._simple_project_creator.run()
        return self

    async def build(self, output_dir: Path) -> Self:
        self._project_compiler.compile_project(
            output_dir=output_dir,
            config=ProjectCompilerConfig(
                hint_validation_disabled=False,
                relative_cairo_path=[],
            ),
        )
        return self

    async def migrate(self, filepath: Path, rollback=False) -> Self:
        migrator = await self._migrator_builder.build(filepath)
        await migrator.run(rollback)
        return self


# pylint: disable=too-many-locals
def build_protostar_fixture(project_root_path: Path, mocker: MockerFixture):
    version_manager = mocker.MagicMock()
    version_manager.protostar_version = mocker.MagicMock()
    version_manager.protostar_version = "99.9.9"

    protostar_toml_path = project_root_path / "protostar.toml"
    protostar_toml_writer = ProtostarTOMLWriter()
    protostar_toml_reader = ProtostarTOMLReader(protostar_toml_path=protostar_toml_path)

    project_cairo_path_builder = ProjectCairoPathBuilder(
        project_root_path=project_root_path,
        project_section_loader=ProtostarProjectSection.Loader(protostar_toml_reader),
    )

    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        project_cairo_path_builder=project_cairo_path_builder,
        contracts_section_loader=ProtostarContractsSection.Loader(
            protostar_toml_reader
        ),
    )

    migrator_builder = Migrator.Builder(
        migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(),
        gateway_facade_builder=GatewayFacade.Builder(project_root_path),
    )

    simple_project_creator = SimpleProjectCreator(
        project_root_path,
        Path(__file__).parent / ".." / "..",
        protostar_toml_writer,
        version_manager,
    )

    ProtostarFixture(
        project_compiler=project_compiler,
        migrator_builder=migrator_builder,
        simple_project_creator=simple_project_creator,
    )


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
