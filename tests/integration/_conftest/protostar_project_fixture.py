import os
from pathlib import Path
from typing import Dict, List, Union, Generator, cast, Any
from contextlib import contextmanager

import pytest
from pytest_mock import MockerFixture

from tests.conftest import ProtostarTmpPathFactory

from protostar.configuration_file import (
    ConfigurationFileV2Model,
    ConfigurationFileV2,
)
from protostar.configuration_file.configuration_toml_interpreter import (
    ConfigurationTOMLInterpreter,
)
from protostar.cairo import CairoVersion
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
from .spying_gateway_facade_factory import SpyingGatewayFacadeFactory
from .transaction_registry import TransactionRegistry

ContractMap = Dict[str, List[str]]

REPOSITORY_ROOT = Path(__file__).parent.parent.parent.parent.resolve()


@contextmanager
# pylint: disable=unused-argument
def fake_activity_indicator(message: str) -> Generator[None, None, None]:
    yield


class ProtostarProjectFixture:
    def __init__(
        self,
        mocker: MockerFixture,
        tmp_path_factory: ProtostarTmpPathFactory,
        cairo_version: CairoVersion = CairoVersion.cairo0,
    ) -> None:
        self._mocker = mocker
        self._tmp_path_factory = tmp_path_factory

        tmp_path = self._tmp_path_factory()
        self._project_root_path = tmp_path

        self.cwd = None
        self.protostar = self.create_protostar_fixture()
        self._create_protostar_project(cairo_version)

    def _create_protostar_project(self, cairo_version: CairoVersion):
        self.cwd = Path().resolve()

        project_name = "project_name"
        if cairo_version == CairoVersion.cairo0:
            self.protostar.init_sync(project_name)
        else:
            self.protostar.init_cairo1_sync(project_name)

        self._project_root_path = self._project_root_path / project_name
        os.chdir(self._project_root_path)
        # rebuilding protostar fixture to reload configuration file
        self.protostar = self.create_protostar_fixture()

    def __enter__(self):
        return self

    def __exit__(self, *args: Any, **kwargs: Any):
        assert self.cwd
        os.chdir(self.cwd)

    def create_protostar_fixture(self):
        version_manager = self._mocker.MagicMock()
        version_manager.protostar_version = self._mocker.MagicMock()
        version_manager.protostar_version = "99.9.9"

        configuration_file = ConfigurationFileFactory(
            active_profile_name=None, cwd=self._project_root_path
        ).create()
        project_cairo_path_builder = ProjectCairoPathBuilder(
            project_root_path=self._project_root_path,
        )

        project_compiler = Cairo0ProjectCompiler(
            project_root_path=self._project_root_path,
            project_cairo_path_builder=project_cairo_path_builder,
            configuration_file=configuration_file,
        )

        input_requester = cast(InputRequester, self._mocker.MagicMock())

        def request_input(message: str) -> str:
            if message.startswith("project directory name"):
                return self._project_root_path.name
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
            output_dir_path=self._project_root_path,
        )

        init_command = InitCommand(
            input_requester,
            new_project_creator=new_project_creator,
            adapted_project_creator=self._mocker.MagicMock(),
        )

        init_cairo1_command = InitCairo1Command(
            new_project_creator=new_project_creator,
        )

        messenger_factory = MessengerFactory(
            log_color_provider=log_color_provider,
            activity_indicator=fake_activity_indicator,
        )

        build_command = BuildCommand(
            project_compiler=project_compiler,
            messenger_factory=messenger_factory,
        )

        build_cairo1_command = BuildCairo1Command(
            configuration_file=project_compiler.configuration_file,
            project_root_path=self._project_root_path,
        )

        transaction_registry = TransactionRegistry()

        gateway_facade_factory = SpyingGatewayFacadeFactory(
            project_root_path=self._project_root_path,
            transaction_registry=transaction_registry,
        )

        deploy_account_command = DeployAccountCommand(
            gateway_facade_factory=gateway_facade_factory,
            messenger_factory=messenger_factory,
        )

        format_command = FormatCommand(
            project_root_path=self._project_root_path,
            messenger_factory=messenger_factory,
        )
        declare_command = DeclareCommand(
            gateway_facade_factory=gateway_facade_factory,
            messenger_factory=messenger_factory,
        )

        deploy_command = DeployCommand(
            gateway_facade_factory=gateway_facade_factory,
            messenger_factory=messenger_factory,
        )

        test_command = TestCommand(
            project_root_path=self._project_root_path,
            protostar_directory=ProtostarDirectory(REPOSITORY_ROOT),
            project_cairo_path_builder=LinkedLibrariesBuilder(),
            log_color_provider=log_color_provider,
            cwd=self._project_root_path,
            active_profile_name=None,
            messenger_factory=messenger_factory,
        )

        invoke_command = InvokeCommand(
            gateway_facade_factory=gateway_facade_factory,
            messenger_factory=messenger_factory,
        )
        call_command = CallCommand(
            project_root_path=self._project_root_path,
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
            project_root_path=self._project_root_path,
            init_command=init_command,
            init_cairo1_command=init_cairo1_command,
            call_command=call_command,
            build_command=build_command,
            build_cairo1_command=build_cairo1_command,
            format_command=format_command,
            declare_command=declare_command,
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

    @property
    def project_root_path(self) -> Path:
        return self._project_root_path

    def create_files(
        self, relative_path_str_to_file: Dict[str, Union[str, Path]]
    ) -> None:
        for relative_path_str, file in relative_path_str_to_file.items():
            if isinstance(file, Path):
                content = file.read_text("utf-8")
            else:
                content = file
            self._save_file(self._project_root_path / relative_path_str, content)

    def create_contracts(self, contract_name_to_file: Dict[str, Union[str, Path]]):
        relative_path_str_to_file = {
            f"src/{contract_name}.cairo": file
            for contract_name, file in contract_name_to_file.items()
        }
        self.create_files(relative_path_str_to_file)
        self.add_contracts_to_protostar_toml(contract_name_to_file)
        self.protostar = self.create_protostar_fixture()

    def add_contracts_to_protostar_toml(
        self, contract_name_to_file: Dict[str, Union[str, Path]]
    ):
        protostar_toml_path = self.project_root_path / "protostar.toml"
        assert (
            protostar_toml_path.is_file()
        ), "No protostar.toml found, cannot change contents."

        interpreter = ConfigurationTOMLInterpreter(
            protostar_toml_path.read_text("utf-8")
        )
        config_file_v2 = ConfigurationFileV2(
            project_root_path=self.project_root_path,
            configuration_file_interpreter=interpreter,
            file_path=protostar_toml_path,
            active_profile_name=None,
        )

        previous_contract_map = {
            contract_name: [
                str(src_path)
                for src_path in config_file_v2.get_contract_source_paths(contract_name)
            ]
            for contract_name in config_file_v2.get_contract_names()
        }

        new_contract_map = {
            contract_name: [str(file_path.resolve())]
            if isinstance(file_path, Path)
            else [file_path]
            for contract_name, file_path in contract_name_to_file.items()
        }

        declared_protostar_v = config_file_v2.get_declared_protostar_version()
        declared_protostar_v_str = (
            str(declared_protostar_v) if declared_protostar_v else None
        )
        overriden_config_file_model_v2 = ConfigurationFileV2Model(
            protostar_version=declared_protostar_v_str,
            contract_name_to_path_strs={
                **previous_contract_map,
                **new_contract_map,
            },
            project_config={},
            command_name_to_config={},
            profile_name_to_project_config={},
            profile_name_to_commands_config={},
        )
        content_factory = ConfigurationFileV2ContentFactory(
            content_builder=ConfigurationTOMLContentBuilder()
        )
        file_content = content_factory.create_file_content(
            overriden_config_file_model_v2
        )
        protostar_toml_path.write_text(file_content)

    @staticmethod
    def _save_file(path: Path, content: str) -> None:
        path.parent.mkdir(exist_ok=True, parents=True)
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(content)
