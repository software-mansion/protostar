from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List

from protostar.cli import Command
from protostar.commands import (
    BuildCommand,
    DeclareCommand,
    DeployCommand,
    InitCommand,
    InstallCommand,
    MigrateCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from protostar.commands.init.project_creator import (
    AdaptedProjectCreator,
    NewProjectCreator,
)
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_cli import ProtostarCLI
from protostar.protostar_toml import (
    ProtostarContractsSection,
    ProtostarProjectSection,
    ProtostarTOMLReader,
    ProtostarTOMLWriter,
    search_upwards_protostar_toml_path,
)
from protostar.protostar_toml.protostar_toml_version_checker import (
    ProtostarTOMLVersionChecker,
)
from protostar.starknet_gateway import GatewayFacade
from protostar.upgrader import (
    LatestVersionCacheTOML,
    LatestVersionChecker,
    LatestVersionRemoteChecker,
    UpgradeManager,
)
from protostar.utils import (
    InputRequester,
    ProtostarDirectory,
    VersionManager,
    log_color_provider,
)


@dataclass
class DIContainer:
    protostar_cli: ProtostarCLI
    protostar_toml_reader: ProtostarTOMLReader


# pylint: disable=too-many-locals
def build_di_container(script_root: Path):
    logger = getLogger()
    cwd = Path().resolve()
    protostar_toml_path = search_upwards_protostar_toml_path(start_path=cwd)
    project_root_path = (
        protostar_toml_path.parent if protostar_toml_path is not None else cwd
    )
    protostar_toml_path = protostar_toml_path or project_root_path / "protostar.toml"
    protostar_directory = ProtostarDirectory(script_root)
    version_manager = VersionManager(protostar_directory, logger)
    protostar_toml_writer = ProtostarTOMLWriter()
    protostar_toml_reader = ProtostarTOMLReader(protostar_toml_path=protostar_toml_path)
    requester = InputRequester(log_color_provider)
    latest_version_checker = LatestVersionChecker(
        protostar_directory=protostar_directory,
        version_manager=version_manager,
        logger=logger,
        log_color_provider=log_color_provider,
        latest_version_cache_toml_reader=LatestVersionCacheTOML.Reader(
            protostar_directory
        ),
        latest_version_cache_toml_writer=LatestVersionCacheTOML.Writer(
            protostar_directory
        ),
        latest_version_remote_checker=LatestVersionRemoteChecker(),
    )
    gateway_facade_builder = GatewayFacade.Builder(project_root_path=project_root_path)

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

    commands: List[Command] = [
        InitCommand(
            requester=requester,
            new_project_creator=NewProjectCreator(
                script_root,
                requester,
                protostar_toml_writer,
                version_manager,
            ),
            adapted_project_creator=AdaptedProjectCreator(
                script_root,
                requester,
                protostar_toml_writer,
                version_manager,
            ),
        ),
        BuildCommand(project_compiler, logger),
        InstallCommand(
            log_color_provider=log_color_provider,
            logger=logger,
            project_root_path=project_root_path,
            project_section_loader=ProtostarProjectSection.Loader(
                protostar_toml_reader
            ),
        ),
        RemoveCommand(
            logger=logger,
            project_root_path=project_root_path,
            project_section_loader=ProtostarProjectSection.Loader(
                protostar_toml_reader
            ),
        ),
        UpdateCommand(
            logger=logger,
            project_root_path=project_root_path,
            project_section_loader=ProtostarProjectSection.Loader(
                protostar_toml_reader
            ),
        ),
        UpgradeCommand(
            UpgradeManager(
                protostar_directory,
                version_manager,
                LatestVersionRemoteChecker(),
                logger,
            ),
            logger=logger,
        ),
        TestCommand(project_root_path, protostar_directory, project_cairo_path_builder),
        DeployCommand(gateway_facade_builder, logger),
        DeclareCommand(gateway_facade_builder, logger),
        MigrateCommand(
            migrator_builder=Migrator.Builder(
                migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(),
                gateway_facade_builder=GatewayFacade.Builder(project_root_path),
                project_root_path=project_root_path,
            ),
            requester=requester,
            logger=logger,
            log_color_provider=log_color_provider,
        ),
    ]
    protostar_toml_version_checker = ProtostarTOMLVersionChecker(
        protostar_toml_reader=protostar_toml_reader, version_manager=version_manager
    )

    protostar_cli = ProtostarCLI(
        commands=commands,
        latest_version_checker=latest_version_checker,
        protostar_toml_version_checker=protostar_toml_version_checker,
        log_color_provider=log_color_provider,
        logger=logger,
        version_manager=version_manager,
    )

    return DIContainer(protostar_cli, protostar_toml_reader)
