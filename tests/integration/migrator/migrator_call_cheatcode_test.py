import pytest

from protostar.starknet_gateway.starknet_request import StarknetRequest


@pytest.fixture(autouse=True, scope="module")
# pylint: disable=unused-argument
def testing_environment(standard_project, compile_project):
    compile_project(
        {
            "main.json": """
                %lang starknet

                @view
                func identity(arg) -> (res : felt):
                    return (arg)
                end
            """
        }
    )


async def test_call_contract(migrate):
    migration_history = await migrate(
        """
        contract_address = deploy("./build/main.json").contract_address
        call(contract_address, "identity", [42])
        """
    )

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
