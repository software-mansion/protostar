from argparse import ArgumentParser
from typing import Any

import pytest
from pytest_mock import MockerFixture

from src.conftest import FooCommand
from src.core import ArgumentParserFacade, ReferenceDocsGenerator
from src.utils.protostar_directory import VersionManager

from .protostar_cli import ROOT_ARGS, SCRIPT_ROOT, ProtostarCLI, protostar_cli
from .protostar_exception import ProtostarException


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


@pytest.mark.asyncio
async def test_should_call_all_provided_commands(
    version_manager: VersionManager, foo_command: FooCommand
):
    # MagicMock doesn't work when awaited
    was_called_ref = {"current": False}

    async def on_run(_args) -> None:
        was_called_ref["current"] = True
        return None

    foo_command.run = on_run

    cli = ProtostarCLI(version_manager, commands=[foo_command], root_args=ROOT_ARGS)
    parser = ArgumentParserFacade(ArgumentParser(), cli)

    result = await cli.run(parser.parse([foo_command.name]))

    assert was_called_ref["current"]
    assert result is True


@pytest.mark.parametrize("git_version", ["2.27"])
@pytest.mark.asyncio
async def test_should_fail_due_to_old_git(
    version_manager: VersionManager, foo_command: FooCommand
):
    cli = ProtostarCLI(version_manager, commands=[foo_command], root_args=ROOT_ARGS)
    parser = ArgumentParserFacade(ArgumentParser(), cli)
    with pytest.raises(ProtostarException):
        await cli.run(parser.parse([foo_command.name]))


def test_instance_matches_cli_reference_docs():
    new_snapshot = ReferenceDocsGenerator(
        protostar_cli
    ).generate_cli_reference_markdown()

    with open(
        SCRIPT_ROOT / "website" / "docs" / "cli-reference.md", "r", encoding="utf-8"
    ) as doc_file:
        snapshot = doc_file.read()
        assert snapshot == new_snapshot, "Snapshot mismatch. Run `poe update_cli_docs`."


@pytest.mark.asyncio
async def test_should_print_protostar_version(
    version_manager: VersionManager, mocker: MockerFixture
):
    version_manager.print_current_version = mocker.MagicMock()
    cli = ProtostarCLI(version_manager, root_args=ROOT_ARGS)
    parser = ArgumentParserFacade(ArgumentParser(), cli)

    await cli.run(parser.parse(["--version"]))

    version_manager.print_current_version.assert_called_once()
