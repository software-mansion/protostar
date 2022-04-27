from asyncio import Future
from logging import Logger
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from src.cli import ArgumentParserFacade, ReferenceDocsGenerator
from src.utils.protostar_directory import VersionManager

from .protostar_cli import ProtostarCLI


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


@pytest.fixture(name="protostar_cli")
def protostar_cli_fixture(
    mocker: MockerFixture, version_manager: VersionManager
) -> ProtostarCLI:
    return ProtostarCLI(
        Path(),
        mocker.MagicMock(),
        mocker.MagicMock(),
        version_manager,
    )


@pytest.mark.parametrize("git_version", ["2.27"])
@pytest.mark.asyncio
async def test_should_fail_due_to_old_git(
    protostar_cli: ProtostarCLI, mocker: MockerFixture
):

    # pylint: disable=protected-access
    protostar_cli._setup_logger = mocker.MagicMock()
    logger_mock = mocker.MagicMock(Logger)
    logger_mock.error = mocker.MagicMock()
    # pylint: disable=protected-access
    protostar_cli._setup_logger.return_value = logger_mock
    parser = ArgumentParserFacade(protostar_cli)

    await protostar_cli.run(parser.parse(["--version"]))

    logger_mock.error.assert_called_once()
    assert "2.28" in logger_mock.error.call_args_list[0][0][0]


def test_instance_matches_cli_reference_docs(protostar_cli: ProtostarCLI):
    new_snapshot = ReferenceDocsGenerator(
        protostar_cli
    ).generate_cli_reference_markdown()

    with open(
        Path(__file__).parent / ".." / "website" / "docs" / "cli-reference.md",
        "r",
        encoding="utf-8",
    ) as doc_file:
        snapshot = doc_file.read()
        assert snapshot == new_snapshot, "Snapshot mismatch. Run `poe update_cli_docs`."


@pytest.mark.asyncio
async def test_should_print_protostar_version(
    protostar_cli: ProtostarCLI, mocker: MockerFixture
):
    protostar_cli.version_manager.print_current_version = mocker.MagicMock()
    parser = ArgumentParserFacade(protostar_cli)

    await protostar_cli.run(parser.parse(["--version"]))

    protostar_cli.version_manager.print_current_version.assert_called_once()


@pytest.mark.asyncio
async def test_should_run_expected_command(
    protostar_cli: ProtostarCLI, mocker: MockerFixture
):
    command = protostar_cli.commands[0]
    command.run = mocker.MagicMock()
    command.run.return_value = Future()
    command.run.return_value.set_result(True)
    parser = ArgumentParserFacade(protostar_cli)

    await protostar_cli.run(parser.parse([command.name]))

    command.run.assert_called_once()


@pytest.mark.asyncio
async def test_should_sys_exit_on_keyboard_interrupt(
    protostar_cli: ProtostarCLI, mocker: MockerFixture
):
    command = protostar_cli.commands[0]
    command.run = mocker.MagicMock()
    command.run.side_effect = KeyboardInterrupt()
    parser = ArgumentParserFacade(protostar_cli)

    with pytest.raises(SystemExit):
        await protostar_cli.run(parser.parse([command.name]))


def test_should_create_instance_of_protostar_cli(tmpdir):
    script_root = Path(tmpdir)
    protostar_cli = ProtostarCLI.create(script_root)
    # pylint: disable=protected-access
    assert (
        protostar_cli.version_manager._protostar_directory.protostar_binary_dir_path
        == script_root
    )
