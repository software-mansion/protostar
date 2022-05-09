import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from src import main


@pytest.fixture(name="protostar_cli_create_mock")
def protostar_cli_create_mock_fixture(mocker: MockerFixture):
    return mocker.patch("src.protostar_cli.ProtostarCLI.create")


@pytest.fixture(name="run_mock")
def run_fixture(mocker: MockerFixture):
    mock = mocker.MagicMock()
    return mock


@pytest.fixture(autouse=True)
def protostar_cli_fixture(
    mocker: MockerFixture, protostar_cli_create_mock: MagicMock, run_mock: MagicMock
):
    mocker.patch("src.start.ArgumentParserFacade")
    protostar_cli_mock = mocker.MagicMock()
    protostar_cli_create_mock.return_value = protostar_cli_mock
    mocker.patch.object(
        protostar_cli_mock, attribute="run", new=asyncio.coroutine(run_mock)
    )


def test_should_run_protostar_cli(run_mock: MagicMock):

    main(Path())

    run_mock.assert_called_once()


def test_should_tell_user_where_to_report_unexpected_errors(
    capsys, run_mock: MagicMock
):
    run_mock.side_effect = Exception()

    with pytest.raises(Exception):
        main(Path())

    captured = capsys.readouterr()
    output = captured.out.split("\n")
    assert "https://github.com/software-mansion/protostar/issues" in output
