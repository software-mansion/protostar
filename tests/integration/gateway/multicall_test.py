from protostar.starknet_gateway.multicall import (
    MulticallUseCase,
    DeployCall,
    InvokeCall,
    MulticallInput,
    CallResolver,
    ResolvedCallsToCalldataConverter,
)
from protostar.starknet_gateway import AccountManager, GatewayFacade
from tests._conftest.devnet import DevnetFixture


async def test_multicall_use_case_happy_case(
    gateway_facade: GatewayFacade, devnet: DevnetFixture
):
    account = devnet.get_predeployed_accounts()[0]
    account_manager = AccountManager(
        private_key=int(account.private_key),
        signer=account.signer,
        address=account.address,
        gateway_url=devnet.get_gateway_url(),
    )
    multicall = MulticallUseCase(
        signer=account_manager,
        gateway=gateway_facade,
        call_resolver=CallResolver(),
        resolved_calls_to_calldata_converter=ResolvedCallsToCalldataConverter(),
    )
    deploy_call = DeployCall(
        class_hash=1,
        calldata=[],
    )
    invoke_call = InvokeCall(
        address="A",
        calldata=[42],
        function_name="increase_balance",
    )
    calls = MulticallInput(calls=[deploy_call, invoke_call])

    result = await multicall.execute(calls)

    await devnet.assert_transaction_accepted(result.transaction_hash)
