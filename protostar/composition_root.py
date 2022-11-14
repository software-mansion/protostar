from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Optional

from protostar.argument_parser import ArgumentParserFacade
from protostar.cli import (
    ProtostarCommand,
    map_protostar_type_name_to_parser,
    MessengerFactory,
)
from protostar.cli.lib_path_resolver import LibPathResolver
from protostar.commands import (
    BuildCommand,
    CalculateAccountAddressCommand,
    CallCommand,
    DeclareCommand,
    DeployAccountCommand,
    DeployCommand,
    FormatCommand,
    InitCommand,
    InstallCommand,
    InvokeCommand,
    MigrateCommand,
    MigrateConfigurationFileCommand,
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
from protostar.configuration_file import (
    ConfigurationFileFactory,
    ConfigurationFileV1,
    ConfigurationFileV2ContentFactory,
    ConfigurationFileV2Migrator,
    ConfigurationTOMLContentBuilder,
)
from protostar.io import InputRequester, log_color_provider
from protostar.migrator import Migrator, MigratorExecutionEnvironment
from protostar.protostar_cli import ProtostarCLI
from protostar.self import ProtostarCompatibilityWithProjectChecker
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
    configuration_file_factory = ConfigurationFileFactory(
        cwd, active_profile_name=active_configuration_profile_name
    )
    configuration_file = configuration_file_factory.create()
    project_root_path = configuration_file.get_filepath().parent

    protostar_directory = ProtostarDirectory(script_root)
    version_manager = VersionManager(protostar_directory, logger)
    protostar_version = version_manager.protostar_version
    input_requester = InputRequester(log_color_provider)
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
        project_root_path=project_root_path, configuration_file=configuration_file
    )

    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        project_cairo_path_builder=project_cairo_path_builder,
        configuration_file=configuration_file,
    )

    gateway_facade_factory = GatewayFacadeFactory(
        project_root_path=project_root_path,
        compiled_contract_reader=CompiledContractReader(),
    )

    lib_path_resolver = LibPathResolver(
        configuration_file=configuration_file,
        project_root_path=project_root_path,
        legacy_mode=isinstance(configuration_file, ConfigurationFileV1),
    )

    configuration_file_content_factory = ConfigurationFileV2ContentFactory(
        content_builder=ConfigurationTOMLContentBuilder()
    )

    new_project_creator = NewProjectCreator(
        script_root=script_root,
        requester=input_requester,
        configuration_file_content_factory=configuration_file_content_factory,
        protostar_version=protostar_version,
    )

    adapted_project_creator = AdaptedProjectCreator(
        script_root,
        configuration_file_content_factory=configuration_file_content_factory,
        protostar_version=protostar_version,
    )

    messenger_factory = MessengerFactory(log_color_provider=log_color_provider)

    migrate_configuration_file_command = MigrateConfigurationFileCommand(
        logger=logger,
        configuration_file_migrator=ConfigurationFileV2Migrator(
            protostar_version=protostar_version,
            current_configuration_file=configuration_file,
            content_factory=ConfigurationFileV2ContentFactory(
                content_builder=ConfigurationTOMLContentBuilder()
            ),
        ),
    )

    calculate_account_address_command = CalculateAccountAddressCommand(logger=logger)

    commands: list[ProtostarCommand] = [
        InitCommand(
            requester=input_requester,
            new_project_creator=new_project_creator,
            adapted_project_creator=adapted_project_creator,
        ),
        BuildCommand(project_compiler, logger),
        InstallCommand(
            log_color_provider=log_color_provider,
            logger=logger,
            project_root_path=project_root_path,
            lib_path_resolver=lib_path_resolver,
        ),
        RemoveCommand(
            logger=logger,
            project_root_path=project_root_path,
            lib_path_resolver=lib_path_resolver,
        ),
        UpdateCommand(
            logger=logger,
            project_root_path=project_root_path,
            lib_path_resolver=lib_path_resolver,
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
            active_profile_name=active_configuration_profile_name,
            cwd=cwd,
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
            requester=input_requester,
            logger=logger,
            log_color_provider=log_color_provider,
            gateway_facade_factory=gateway_facade_factory,
        ),
        FormatCommand(
            project_root_path=project_root_path,
            messenger_factory=messenger_factory,
        ),
        CairoMigrateCommand(script_root, logger),
        InvokeCommand(gateway_facade_factory=gateway_facade_factory, logger=logger),
        CallCommand(
            gateway_facade_factory=gateway_facade_factory,
            logger=logger,
            messenger_factory=messenger_factory,
        ),
        DeployAccountCommand(
            gateway_facade_factory=gateway_facade_factory, logger=logger
        ),
        migrate_configuration_file_command,
        calculate_account_address_command,
    ]

    compatibility_checker = ProtostarCompatibilityWithProjectChecker(
        protostar_version=protostar_version,
        declared_protostar_version_provider=configuration_file,
    )

    protostar_cli = ProtostarCLI(
        commands=commands,
        latest_version_checker=latest_version_checker,
        log_color_provider=log_color_provider,
        logger=logger,
        version_manager=version_manager,
        project_cairo_path_builder=project_cairo_path_builder,
        configuration_file=configuration_file,
        compatibility_checker=compatibility_checker,
        start_time=start_time,
    )
    if configuration_file:
        configuration_file.set_command_names_provider(protostar_cli)

    argument_parser_facade = ArgumentParserFacade(
        protostar_cli,
        configuration_file,
        parser_resolver=map_protostar_type_name_to_parser,
    )

    return DIContainer(protostar_cli, argument_parser_facade)
