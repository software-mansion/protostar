from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from protostar.commands.declare.declare_command import DeclareCommand
from protostar.starknet_gateway import GatewayFacade


@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
):
    declare_command = DeclareCommand(
        gateway_facade=GatewayFacade(project_root_path), logger=mocker.MagicMock()
    )
    args = SimpleNamespace()
    args.contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.network = None
    args.token = None
    args.signature = None

    response = await declare_command.run(args)

    assert response.class_hash is not None
