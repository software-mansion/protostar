import asyncio
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from .main import main


@pytest.mark.asyncio
def test_should_run_protostar_cli(mocker: MockerFixture):
    mocker.patch("src.cli.ArgumentParserFacade")
    protostar_cli_create_mock = mocker.patch("src.protostar_cli.ProtostarCLI.create")
    protostar_cli_mock = mocker.MagicMock()
    protostar_cli_create_mock.return_value = protostar_cli_mock
    run_mock = mocker.MagicMock()
    mocker.patch.object(
        protostar_cli_mock, attribute="run", new=asyncio.coroutine(run_mock)
    )

    main(Path())

    run_mock.assert_called_once()


# test_should_tell_user_where_to_report_unexpected_errors

# test_should_handle_no_git_scenario
