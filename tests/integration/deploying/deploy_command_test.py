from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.starknet_gateway import GatewayFacade
from protostar.starknet_gateway.network_config import NetworkConfig


@pytest.mark.asyncio
@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
):
    deploy_command = DeployCommand(
        gateway_facade=GatewayFacade(project_root_path),
        network_config_builder=NetworkConfig.Builder(),
        logger=mocker.MagicMock(),
    )
    args = SimpleNamespace()
    args.contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.inputs = ["42"]
    args.network = None
    args.token = None
    args.salt = None

    response = await deploy_command.run(args)

    assert response.address is not None
