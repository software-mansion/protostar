# pylint: disable=consider-using-with


import pytest

from protostar.commands.deploy.starkware.starknet_cli import deploy


@pytest.mark.asyncio
async def test_deploying_contract(
    devnet_gateway_url: str, compiled_contract_file_handle
):
    response = await deploy(
        gateway_url=devnet_gateway_url,
        compiled_contract_file=compiled_contract_file_handle,
    )

    assert response.address is not None
