import asyncio
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from protostar import main
from protostar.composition_root import DIContainer
from protostar.protostar_cli import ProtostarCLI


@pytest.fixture(name="protostar_cli")
def protostar_cli_fixture(mocker: MockerFixture) -> ProtostarCLI:
    return mocker.MagicMock()


@pytest.fixture(name="di_container", autouse=True)
def di_container_patch(mocker: MockerFixture, protostar_cli: ProtostarCLI):
    build_di_container = mocker.patch("protostar.start.build_di_container")
    build_di_container.return_value = DIContainer(
        protostar_cli=protostar_cli,
        argument_value_from_config_provider=mocker.MagicMock(),
    )


@pytest.fixture(name="argument_parser_facade", autouse=True)
def argument_parser_facade_patch(mocker: MockerFixture):
    mocker.patch("protostar.start.ArgumentParserFacade")


@pytest.fixture(name="protostar_cli_run")
def protostar_cli_run_fixture(mocker: MockerFixture, protostar_cli: ProtostarCLI):
    protostar_cli_run_mock = mocker.MagicMock()
    protostar_cli.run = asyncio.coroutine(protostar_cli_run_mock)
    return protostar_cli_run_mock


def test_should_run_protostar_cli(protostar_cli_run: MagicMock):
    main(Path())

    protostar_cli_run.assert_called_once()


def test_should_tell_user_where_to_report_unexpected_errors(
    capsys, protostar_cli_run: MagicMock
):
    protostar_cli_run.side_effect = Exception()

    with pytest.raises(Exception):
        main(Path())

    captured = capsys.readouterr()
    output = captured.out.split("\n")
    assert "https://github.com/software-mansion/protostar/issues" in output
