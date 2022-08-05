from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from protostar.commands.deploy.deploy_command import DeployCommand
from protostar.starknet_gateway import GatewayFacade


@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
):
    deploy_command = DeployCommand(
        gateway_facade_builder=GatewayFacade.Builder(project_root_path),
        logger=mocker.MagicMock(),
    )
    args = SimpleNamespace()
    args.contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.inputs = [42]
    args.network = None
    args.token = None
    args.salt = None
    args.wait_for_acceptance = False

    response = await deploy_command.run(args)

    assert response.address is not None
