import asyncio
from pathlib import Path
from typing import List, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from .main import main


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
    mocker.patch("src.cli.ArgumentParserFacade")
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


def test_handling_no_git_error(capsys, protostar_cli_create_mock: MagicMock):
    protostar_cli_create_mock.side_effect = ImportError(
        "Failed to initialize: Bad git executable."
    )

    with pytest.raises(SystemExit):
        main(Path())

    captured = capsys.readouterr()
    output = cast(List[str], captured.out.split("\n"))
    assert output[0].startswith("Protostar requires git")
