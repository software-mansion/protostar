from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import List, Optional

from protostar.cli import ArgumentParserFacade, Command
from protostar.commands import (
    BuildCommand,
    DeclareCommand,
    DeployCommand,
    FormatCommand,
    InitCommand,
    InstallCommand,
    InvokeCommand,
    MigrateCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from protostar.commands.cairo_migrate_command import CairoMigrateCommand
from protostar.commands.init.project_creator import (
    AdaptedProjectCreator,
    NewProjectCreator,
)
from protostar.compiler import ProjectCairoPathBuilder, ProjectCompiler
from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.configuration_file import ConfigurationFileFactory
from protostar.io import InputRequester, log_color_provider
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_cli import ProtostarCLI
from protostar.protostar_toml import (
    ProtostarContractsSection,
    ProtostarProjectSection,
    ProtostarTOMLReader,
    ProtostarTOMLWriter,
    search_upwards_protostar_toml_path,
)
from protostar.self.protostar_directory import ProtostarDirectory, VersionManager
from protostar.starknet_gateway import GatewayFacadeFactory
from protostar.upgrader import (
    LatestVersionCacheTOML,
    LatestVersionChecker,
    LatestVersionRemoteChecker,
    UpgradeManager,
)


@dataclass
class DIContainer:
    protostar_cli: ProtostarCLI
    argument_parser_facade: ArgumentParserFacade


def build_di_container(
    script_root: Path,
    active_configuration_profile_name: Optional[str] = None,
    start_time: float = 0,
):
    logger = getLogger()
    cwd = Path().resolve()
    protostar_toml_path = search_upwards_protostar_toml_path(start_path=cwd)
    project_root_path = (
        protostar_toml_path.parent if protostar_toml_path is not None else cwd
    )
    protostar_toml_path = protostar_toml_path or project_root_path / "protostar.toml"

    configuration_file_factory = ConfigurationFileFactory(
        cwd, active_profile_name=active_configuration_profile_name
    )
    configuration_file = configuration_file_factory.create()

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

    gateway_facade_factory = GatewayFacadeFactory(
        project_root_path=project_root_path,
        compiled_contract_reader=CompiledContractReader(),
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
        TestCommand(
            project_root_path,
            protostar_directory,
            project_cairo_path_builder,
            logger=logger,
            log_color_provider=log_color_provider,
        ),
        DeployCommand(
            logger=logger,
            gateway_facade_factory=gateway_facade_factory,
        ),
        DeclareCommand(logger=logger, gateway_facade_factory=gateway_facade_factory),
        MigrateCommand(
            migrator_builder=Migrator.Builder(
                migrator_execution_environment_builder=MigratorExecutionEnvironment.Builder(
                    project_compiler
                ),
                project_root_path=project_root_path,
            ),
            requester=requester,
            logger=logger,
            log_color_provider=log_color_provider,
            gateway_facade_factory=gateway_facade_factory,
        ),
        FormatCommand(project_root_path, logger),
        CairoMigrateCommand(script_root, logger),
        InvokeCommand(gateway_facade_factory=gateway_facade_factory, logger=logger),
    ]

    protostar_cli = ProtostarCLI(
        commands=commands,
        latest_version_checker=latest_version_checker,
        log_color_provider=log_color_provider,
        logger=logger,
        version_manager=version_manager,
        project_cairo_path_builder=project_cairo_path_builder,
        start_time=start_time,
    )
    if configuration_file:
        configuration_file.set_command_names_provider(protostar_cli)

    argument_parser_facade = ArgumentParserFacade(protostar_cli, configuration_file)

    return DIContainer(protostar_cli, argument_parser_facade)
