import pytest

from protostar.commands.deploy.deploy_contract import deploy_contract


@pytest.mark.asyncio
async def test_deploying_contract(devnet_gateway_url: str, compiled_contract_file):
    response = await deploy_contract(
        gateway_url=devnet_gateway_url, compiled_contract_file=compiled_contract_file
    )

    assert response["address"] is not None
