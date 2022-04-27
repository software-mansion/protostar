import asyncio
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.cli import ArgumentParserFacade
from src.protostar_cli import ProtostarCLI

from .main import main


@pytest.mark.asyncio
def test_should_run_protostar_cli(mocker: MockerFixture):
    protostar_cli = ProtostarCLI.create(Path())
    args = ArgumentParserFacade(protostar_cli).parse(["init"])

    argument_parser_facade_mock = mocker.patch("src.cli.ArgumentParserFacade")
    # argument_parser_facade_mock.parse = mocker.MagicMock()

    protostar_cli_create_mock = mocker.patch("src.protostar_cli.ProtostarCLI.create")
    protostar_cli_mock = mocker.MagicMock()
    protostar_cli_create_mock.return_value = protostar_cli_mock
    run_mock = mocker.MagicMock()
    mocker.patch.object(
        protostar_cli_mock, attribute="run", new=asyncio.coroutine(run_mock)
    )

    protostar_cli = ProtostarCLI.create(Path())
    argument_parser_facade_mock.parse.return_value = args

    main(Path())

    run_mock.assert_called_once()


# test_should_tell_user_where_to_report_unexpected_errors

# test_should_handle_no_git_scenario
