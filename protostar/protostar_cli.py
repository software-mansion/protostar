# pylint: disable=no-self-use
import sys
from logging import INFO, Logger, StreamHandler, getLogger
from pathlib import Path
from typing import Any

from protostar.cli import CLIApp, Command
from protostar.commands import (
    BuildCommand,
    DeployCommand,
    InitCommand,
    InstallCommand,
    RemoveCommand,
    TestCommand,
    UpdateCommand,
    UpgradeCommand,
)
from protostar.commands.build import ProjectCompiler
from protostar.commands.init.project_creator import (
    AdaptedProjectCreator,
    NewProjectCreator,
)
from protostar.protostar_exception import ProtostarException, ProtostarExceptionSilent
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.protostar_toml.protostar_contracts_section import (
    ProtostarContractsSection,
)
from protostar.protostar_toml.protostar_project_section import ProtostarProjectSection
from protostar.upgrader import (
    UpgradeInfoWriterThread,
    UpgradeLocalChecker,
    UpgradeManager,
    UpgradeRemoteChecker,
)
from protostar.upgrader.upgrade_toml import UpgradeTOML
from protostar.utils import (
    Project,
    ProtostarDirectory,
    StandardLogFormatter,
    VersionManager,
    log_color_provider,
)
from protostar.utils.input_requester import InputRequester

PROFILE_ARG = Command.Argument(
    name="profile",
    short_name="p",
    type="str",
    description="\n".join(
        [
            "Specifies active profile configuration. This argument can't be configured in `protostar.toml`.",
            "#### CI configuration",
            '```toml title="protostar.toml"',
            "[profile.ci.protostar.shared_command_configs]",
            "no_color=true",
            "```",
            "`protostar -p ci test`",
            "",
            "#### Deployment configuration",
            '```toml title="protostar.toml"',
            "[profile.devnet.protostar.deploy]",
            'gateway_url="http://127.0.0.1:5050/"',
            "```",
            "`protostar -p devnet deploy ...`" "",
        ]
    ),
)


class ConfigurationProfileCLISchema(CLIApp):
    def __init__(self) -> None:
        super().__init__(
            commands=[],
            root_args=[PROFILE_ARG],
        )


class ProtostarCLI(CLIApp):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        script_root: Path,
        protostar_directory: ProtostarDirectory,
        project: Project,
        version_manager: VersionManager,
        protostar_toml_writer: ProtostarTOMLWriter,
        protostar_toml_reader: ProtostarTOMLReader,
        requester: InputRequester,
        logger: Logger,
        upgrade_local_checker: UpgradeLocalChecker,
        upgrade_info_writer_thread: UpgradeInfoWriterThread,
    ) -> None:
        self.project = project
        self.logger = logger
        self.upgrade_local_checker = upgrade_local_checker
        self.upgrade_info_writer_thread = upgrade_info_writer_thread

        super().__init__(
            commands=[
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
                BuildCommand(
                    ProjectCompiler(
                        project_section_loader=ProtostarProjectSection.Loader(
                            protostar_toml_reader
                        ),
                        contracts_section_loader=ProtostarContractsSection.Loader(
                            protostar_toml_reader
                        ),
                    )
                ),
                InstallCommand(project),
                RemoveCommand(project),
                UpdateCommand(project),
                UpgradeCommand(
                    UpgradeManager(
                        protostar_directory,
                        version_manager,
                        UpgradeRemoteChecker(protostar_directory, version_manager),
                        self.logger,
                    )
                ),
                TestCommand(project, protostar_directory),
                DeployCommand(project),
            ],
            root_args=[
                PROFILE_ARG,
                Command.Argument(
                    name="version",
                    short_name="v",
                    type="bool",
                    description="Show Protostar and Cairo-lang version.",
                ),
                Command.Argument(
                    name="no-color",
                    type="bool",
                    description="Disable colors.",
                ),
            ],
        )
        self.version_manager = version_manager

    @classmethod
    def create(cls, script_root: Path):
        protostar_directory = ProtostarDirectory(script_root)
        version_manager = VersionManager(protostar_directory)
        project = Project(version_manager)
        protostar_toml_writer = ProtostarTOMLWriter()
        protostar_toml_reader = ProtostarTOMLReader()
        requester = InputRequester(log_color_provider)
        logger = getLogger()
        upgrade_local_checker = UpgradeLocalChecker(
            protostar_directory,
            version_manager,
            logger,
            log_color_provider,
            upgrade_toml_reader=UpgradeTOML.Reader(protostar_directory),
        )
        upgrade_info_writer_thread = UpgradeInfoWriterThread(
            UpgradeRemoteChecker(protostar_directory, version_manager),
            UpgradeTOML.Writer(protostar_directory),
        )

        return cls(
            script_root=script_root,
            protostar_directory=protostar_directory,
            project=project,
            version_manager=version_manager,
            protostar_toml_writer=protostar_toml_writer,
            protostar_toml_reader=protostar_toml_reader,
            requester=requester,
            logger=logger,
            upgrade_local_checker=upgrade_local_checker,
            upgrade_info_writer_thread=upgrade_info_writer_thread,
        )

    def _setup_logger(self, is_ci_mode: bool) -> None:
        log_color_provider.is_ci_mode = is_ci_mode
        self.logger.setLevel(INFO)
        handler = StreamHandler()
        handler.setFormatter(StandardLogFormatter(log_color_provider))
        self.logger.addHandler(handler)

    def _check_git_version(self):
        git_version = self.version_manager.git_version
        if git_version and git_version < VersionManager.parse("2.28"):
            raise ProtostarException(
                f"Protostar requires version 2.28 or greater of Git (current version: {git_version})"
            )

    async def run(self, args: Any) -> None:
        self._setup_logger(args.no_color)
        try:
            self.upgrade_local_checker.log_info_if_update_available()
            self._check_git_version()

            if args.version:
                self.version_manager.print_current_version()
                return

            with self.upgrade_info_writer_thread:
                await super().run(args)

        except ProtostarExceptionSilent:
            sys.exit(1)
        except ProtostarException as err:
            if err.details:
                print(err.details)
            self.logger.error(err.message)
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
