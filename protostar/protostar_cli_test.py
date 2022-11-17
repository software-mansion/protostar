import logging
import re
from asyncio import Future
from typing import Any, Protocol, cast

import pytest
from pytest import LogCaptureFixture
from pytest_mock import MockerFixture
from re_assert import Matches

from protostar.argument_parser import ArgumentParserFacade
from protostar.cli import ProtostarCommand
from protostar.io.log_color_provider import LogColorProvider
from protostar.protostar_cli import ProtostarCLI
from protostar.protostar_exception import ProtostarException, ProtostarExceptionSilent
from protostar.self import CompatibilityCheckOutput, CompatibilityResult, VersionManager
from protostar.self.conftest import FakeProtostarCompatibilityWithProjectChecker
from protostar.upgrader.latest_version_checker import LatestVersionChecker


@pytest.fixture(name="git_version")
def git_version_fixture() -> str:
    return "2.29"


@pytest.fixture(name="version_manager")
def version_manager_fixture(mocker: MockerFixture, git_version: str):
    version_manager: Any = VersionManager(mocker.MagicMock())
    type(version_manager).git_version = mocker.PropertyMock(
        return_value=VersionManager.parse(git_version)
    )
    return version_manager


@pytest.fixture(name="commands")
def commands_fixture(mocker: MockerFixture) -> list[ProtostarCommand]:
    command = mocker.MagicMock()
    command.name = "command-name"
    return [command]


@pytest.fixture(name="latest_version_checker")
def latest_version_checker_fixture(mocker: MockerFixture) -> LatestVersionChecker:
    latest_version_checker = cast(LatestVersionChecker, mocker.MagicMock())
    latest_version_checker.run = mocker.MagicMock()
    latest_version_checker.run.return_value = Future()
    latest_version_checker.run.return_value.set_result(None)
    return latest_version_checker


@pytest.fixture(name="protostar_cli")
def protostar_cli_fixture(
    mocker: MockerFixture,
    version_manager: VersionManager,
    commands: list[ProtostarCommand],
    latest_version_checker: LatestVersionChecker,
) -> ProtostarCLI:
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = True
    return ProtostarCLI(
        commands=commands,
        log_color_provider=log_color_provider,
        version_manager=version_manager,
        latest_version_checker=latest_version_checker,
        configuration_file=mocker.MagicMock(),
        project_cairo_path_builder=mocker.MagicMock(),
        compatibility_checker=FakeProtostarCompatibilityWithProjectChecker(
            result=CompatibilityCheckOutput(
                compatibility_result=CompatibilityResult.COMPATIBLE,
                protostar_version_str="0.0.0",
                declared_protostar_version_str="0.0.0",
            )
        ),
    )


class RunProtostarCLIFixture(Protocol):
    async def __call__(self, compatibility_result: CompatibilityResult) -> None:
        ...


@pytest.fixture(name="run_protostar_cli")
def run_protostar_cli_fixture(
    mocker: MockerFixture,
    version_manager: VersionManager,
    latest_version_checker: LatestVersionChecker,
    commands: list[ProtostarCommand],
) -> RunProtostarCLIFixture:
    async def run_protostar_command(compatibility_result: CompatibilityResult):
        command = commands[0]
        command.run = mocker.MagicMock()
        command.run.return_value = Future()
        command.run.return_value.set_result(True)
        log_color_provider = LogColorProvider()
        log_color_provider.is_ci_mode = True
        protostar_cli = ProtostarCLI(
            commands=commands,
            log_color_provider=log_color_provider,
            version_manager=version_manager,
            latest_version_checker=latest_version_checker,
            configuration_file=mocker.MagicMock(),
            project_cairo_path_builder=mocker.MagicMock(),
            compatibility_checker=FakeProtostarCompatibilityWithProjectChecker(
                result=CompatibilityCheckOutput(
                    compatibility_result=compatibility_result,
                    protostar_version_str="0.0.0",
                    declared_protostar_version_str="0.0.0",
                )
            ),
        )
        parser = ArgumentParserFacade(protostar_cli)

        await protostar_cli.run(parser.parse([command.name]))

    return run_protostar_command


@pytest.mark.parametrize("git_version", ["2.27"])
async def test_should_fail_due_to_old_git(
    protostar_cli: ProtostarCLI, caplog: LogCaptureFixture
):
    parser = ArgumentParserFacade(protostar_cli)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit) as ex:
            await protostar_cli.run(parser.parse(["--version"]))
            assert cast(SystemExit, ex).code == 1

        assert caplog.record_tuples == [("root", logging.ERROR, Matches(r".*2\.28.*"))]


async def test_should_print_protostar_version(
    protostar_cli: ProtostarCLI, mocker: MockerFixture, version_manager: VersionManager
):
    version_manager.print_current_version = mocker.MagicMock()
    parser = ArgumentParserFacade(protostar_cli)

    await protostar_cli.run(parser.parse(["--version"]))

    version_manager.print_current_version.assert_called_once()


async def test_should_run_expected_command(
    protostar_cli: ProtostarCLI, mocker: MockerFixture, commands: list[ProtostarCommand]
):
    command = commands[0]
    command.run = mocker.MagicMock()
    command.run.return_value = Future()
    command.run.return_value.set_result(True)
    parser = ArgumentParserFacade(protostar_cli)

    command.run.assert_not_called()

    await protostar_cli.run(parser.parse([command.name]))

    command.run.assert_called_once()


async def test_should_sys_exit_on_keyboard_interrupt(
    protostar_cli: ProtostarCLI, mocker: MockerFixture, commands: list[ProtostarCommand]
):
    command = commands[0]
    command.run = mocker.MagicMock()
    command.run.side_effect = KeyboardInterrupt()
    parser = ArgumentParserFacade(protostar_cli)

    with pytest.raises(SystemExit) as ex:
        await protostar_cli.run(parser.parse([command.name]))
        assert cast(SystemExit, ex).code == 1


async def test_should_sys_exit_on_protostar_exception(
    protostar_cli: ProtostarCLI, mocker: MockerFixture, commands: list[ProtostarCommand]
):
    command = commands[0]
    command.run = mocker.MagicMock()
    command.run.side_effect = ProtostarException("Something")
    parser = ArgumentParserFacade(protostar_cli)

    with pytest.raises(SystemExit) as ex:
        await protostar_cli.run(parser.parse([command.name]))
        assert cast(SystemExit, ex).code == 1


async def test_should_sys_exit_on_protostar_silent_exception(
    protostar_cli: ProtostarCLI, mocker: MockerFixture, commands: list[ProtostarCommand]
):
    command = commands[0]
    command.run = mocker.MagicMock()
    command.run.side_effect = ProtostarExceptionSilent("Something")
    parser = ArgumentParserFacade(protostar_cli)

    with pytest.raises(SystemExit) as ex:
        await protostar_cli.run(parser.parse([command.name]))
        assert cast(SystemExit, ex).code == 1


async def test_getting_command_names(
    protostar_cli: ProtostarCLI, commands: list[ProtostarCommand]
):
    command_names = protostar_cli.get_command_names()

    assert command_names == [command.name for command in commands]


@pytest.mark.parametrize(
    "compatibility_result, expected_warnings",
    [
        (CompatibilityResult.COMPATIBLE, []),
        (
            CompatibilityResult.OUTDATED_DECLARED_VERSION,
            [
                (
                    "root",
                    logging.WARNING,
                    Matches(r".*update the declared Protostar version.*", flags=re.S),
                )
            ],
        ),
        (
            CompatibilityResult.OUTDATED_PROTOSTAR,
            [("root", logging.WARNING, Matches(".*upgrade Protostar.*", flags=re.S))],
        ),
    ],
)
async def test_checking_compatibility(
    caplog: LogCaptureFixture,
    run_protostar_cli: RunProtostarCLIFixture,
    compatibility_result: CompatibilityResult,
    expected_warnings: list[tuple[str, int, str]],
):
    with caplog.at_level(logging.WARNING):
        await run_protostar_cli(compatibility_result)

        assert caplog.record_tuples == expected_warnings
