from pathlib import Path
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture
from starknet_py.net.models import StarknetChainId

from protostar.commands.deploy.deploy_command import DeployCommand


@pytest.mark.parametrize("contract_name", ["main_with_constructor"])
async def test_deploying_contract(
    mocker: MockerFixture,
    devnet_gateway_url: str,
    project_root_path: Path,
    compiled_contract_filepath,
):
    deploy_command = DeployCommand(
        logger=mocker.MagicMock(),
        project_root_path=project_root_path,
    )
    args = SimpleNamespace()
    args.contract = compiled_contract_filepath
    args.gateway_url = devnet_gateway_url
    args.inputs = [42]
    args.network = None
    args.token = None
    args.salt = None
    args.wait_for_acceptance = False
    args.chain_id = StarknetChainId.TESTNET

    response = await deploy_command.run(args)

    assert response.address is not None
