from protostar.starknet_gateway.starknet_request import StarknetRequest
from tests.integration.migrator.conftest import (
    ContractMainWithConstructorDefaults,
    RunMigrateFixture,
)


async def test_call_contract(run_migrate: RunMigrateFixture):
    migration_history = await run_migrate("migration_deploy_and_call.cairo")

    contract_address = extract_contract_address_from_deploy_response(
        migration_history.starknet_requests[0].response
    )
    call_request = migration_history.starknet_requests[1]
    assert call_request.action == "CALL"
    assert call_request.payload["inputs"] == "[]"
    assert call_request.payload["contract_address"] == str(contract_address)
    assert (
        call_request.response["response"]
        == ContractMainWithConstructorDefaults.INITIAL_BALANCE
    )


def extract_contract_address_from_deploy_response(
    deploy_response: StarknetRequest.Payload,
) -> int:
    assert isinstance(deploy_response["contract_address"], int)
    return deploy_response["contract_address"]
