from contextlib import contextmanager
from pathlib import Path
from typing import Generator, cast

import pytest
from pytest_mock import MockerFixture

from protostar.argument_parser import ArgumentParserFacade, CLIApp
from protostar.cli import map_protostar_type_name_to_parser, MessengerFactory
from protostar.commands import (
    BuildCommand,
    BuildCairo1Command,
    CalculateAccountAddressCommand,
    CallCommand,
    DeclareCommand,
    FormatCommand,
    InitCommand,
    InitCairo1Command,
    InvokeCommand,
    MulticallCommand,
    DeclareCairo1Command,
)
from protostar.commands.deploy_account_command import DeployAccountCommand
from protostar.commands.deploy_command import DeployCommand
from protostar.commands.init.project_creator.new_project_creator import (
    NewProjectCreator,
)
from protostar.commands.test import TestCommand
from protostar.compiler import (
    ProjectCairoPathBuilder,
    LinkedLibrariesBuilder,
    Cairo0ProjectCompiler,
    ProjectCompiler,
)
from protostar.configuration_file import (
    ConfigurationFileFactory,
    ConfigurationFileV2ContentFactory,
    ConfigurationTOMLContentBuilder,
)
from protostar.io import log_color_provider
from protostar.io.input_requester import InputRequester
from protostar.self.protostar_compatibility_with_project_checker import (
    parse_protostar_version,
)
from protostar.self.protostar_directory import ProtostarDirectory
from .protostar_fixture import ProtostarFixture
from .transaction_registry import TransactionRegistry
from .spying_gateway_facade_factory import SpyingGatewayFacadeFactory


@contextmanager
# pylint: disable=unused-argument
def fake_activity_indicator(message: str) -> Generator[None, None, None]:
    yield


REPOSITORY_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


def create_protostar_fixture(
    mocker: MockerFixture,
    project_root_path: Path,
):
    version_manager = mocker.MagicMock()
    version_manager.protostar_version = mocker.MagicMock()
    version_manager.protostar_version = "99.9.9"

    configuration_file = ConfigurationFileFactory(
        active_profile_name=None, cwd=project_root_path
    ).create()
    project_cairo_path_builder = ProjectCairoPathBuilder(
        project_root_path=project_root_path,
    )

    cairo0_project_compiler = Cairo0ProjectCompiler(
        project_root_path=project_root_path,
        project_cairo_path_builder=project_cairo_path_builder,
        configuration_file=configuration_file,
    )
    project_compiler = ProjectCompiler(
        project_root_path=project_root_path,
        configuration_file=configuration_file,
    )

    input_requester = cast(InputRequester, mocker.MagicMock())

    def request_input(message: str) -> str:
        if message.startswith("project directory name"):
            return project_root_path.name
        if message.startswith("libraries directory name"):
            return "lib"
        return ""

    input_requester.request_input = request_input

    configuration_file_content_factory = ConfigurationFileV2ContentFactory(
        content_builder=ConfigurationTOMLContentBuilder()
    )

    new_project_creator = NewProjectCreator(
        script_root=REPOSITORY_ROOT,
        requester=input_requester,
        configuration_file_content_factory=configuration_file_content_factory,
        protostar_version=parse_protostar_version("0.0.0"),
        output_dir_path=project_root_path,
    )

    init_command = InitCommand(
        input_requester,
        new_project_creator=new_project_creator,
        adapted_project_creator=mocker.MagicMock(),
    )

    init_cairo1_command = InitCairo1Command(
        new_project_creator=new_project_creator,
    )

    messenger_factory = MessengerFactory(
        log_color_provider=log_color_provider,
        activity_indicator=fake_activity_indicator,
    )

    build_command = BuildCommand(
        project_compiler=cairo0_project_compiler,
        messenger_factory=messenger_factory,
    )

    build_cairo1_command = BuildCairo1Command(
        configuration_file=cairo0_project_compiler.configuration_file,
        project_root_path=project_root_path,
    )

    transaction_registry = TransactionRegistry()

    gateway_facade_factory = SpyingGatewayFacadeFactory(
        project_root_path=project_root_path,
        transaction_registry=transaction_registry,
    )

    deploy_account_command = DeployAccountCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    format_command = FormatCommand(
        project_root_path=project_root_path,
        messenger_factory=messenger_factory,
    )
    declare_command = DeclareCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )
    declare_cairo1_command = DeclareCairo1Command(
        project_compiler=project_compiler,
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    deploy_command = DeployCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    test_command = TestCommand(
        project_root_path=project_root_path,
        protostar_directory=ProtostarDirectory(REPOSITORY_ROOT),
        project_cairo_path_builder=LinkedLibrariesBuilder(),
        log_color_provider=log_color_provider,
        cwd=project_root_path,
        active_profile_name=None,
        messenger_factory=messenger_factory,
    )

    invoke_command = InvokeCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )
    call_command = CallCommand(
        project_root_path=project_root_path,
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )
    calculate_account_address_command = CalculateAccountAddressCommand(
        messenger_factory=messenger_factory
    )
    multicall_command = MulticallCommand(
        gateway_facade_factory=gateway_facade_factory,
        messenger_factory=messenger_factory,
    )

    cli_app = CLIApp(
        commands=[
            deploy_account_command,
            calculate_account_address_command,
            multicall_command,
        ]
    )
    parser = ArgumentParserFacade(
        cli_app, parser_resolver=map_protostar_type_name_to_parser
    )

    protostar_fixture = ProtostarFixture(
        project_root_path=project_root_path,
        init_command=init_command,
        init_cairo1_command=init_cairo1_command,
        call_command=call_command,
        build_command=build_command,
        build_cairo1_command=build_cairo1_command,
        format_command=format_command,
        declare_command=declare_command,
        declare_cairo1_command=declare_cairo1_command,
        deploy_command=deploy_command,
        test_command=test_command,
        invoke_command=invoke_command,
        deploy_account_command=deploy_account_command,
        cli_app=cli_app,
        parser=parser,
        transaction_registry=transaction_registry,
        calculate_account_address_command=calculate_account_address_command,
        multicall_command=multicall_command,
        monkeypatch=pytest.MonkeyPatch(),
    )

    return protostar_fixture
