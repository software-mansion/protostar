import asyncio

import pytest

from protostar.starknet_gateway.starknet_request import StarknetRequest
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(scope="module")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True, scope="module")
# pylint: disable=unused-argument
async def setup(protostar: ProtostarFixture):
    await protostar.init()
    protostar.create_files(
        {
            "./src/main.json": """
                %lang starknet

                @view
                func identity(arg) -> (res : felt):
                    return (arg)
                end
            """
        }
    )
    await protostar.build()


async def test_call_contract(protostar: ProtostarFixture, devnet_gateway_url: str):
    file_path = protostar.create_migration(
        """
        contract_address = deploy_contract("./build/main.json").contract_address
        call(contract_address, "identity", [42])
        """
    )

    migration_history = await protostar.migrate(file_path, network=devnet_gateway_url)

    contract_address = extract_contract_address_from_deploy_response(
        migration_history.starknet_requests[0].response
    )
    call_request = migration_history.starknet_requests[1]
    assert call_request.action == "CALL"
    assert call_request.payload["inputs"] == "[]"
    assert call_request.payload["contract_address"] == str(contract_address)
    assert call_request.response["response"] == "42"


def extract_contract_address_from_deploy_response(
    deploy_response: StarknetRequest.Payload,
) -> int:
    assert isinstance(deploy_response["contract_address"], int)
    return deploy_response["contract_address"]
