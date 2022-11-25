from protostar.starknet_gateway.multicall import (
    MulticallUseCase,
    DeployCall,
    InvokeCall,
    MulticallInput,
)
from protostar.starknet_gateway import AccountManager
from tests._conftest.devnet import DevnetFixture


async def test_multicall_use_case_happy_case(
    gateway_facade: GatewayFacade, devnet: DevnetFixture
):
    account = devnet.get_predeployed_accounts()[0]
    account_manager = AccountManager(
        private_key=account.private_key,
        signer=account.signer,
    )
    multicall = MulticallUseCase(
        signer=account_manager,
        gateway=gateway_facade,
    )
    deploy_call = DeployCall(
        compiled_contract="...",
        calldata=[],
        max_fee="auto",
    )
    invoke_call = InvokeCall(
        compiled_contract="...",
        address="FROM_DEPLOY",
        calldata=[42],
        function_name="increase_balance",
        max_fee="auto",
    )
    calls = MulticallInput(calls=[deploy_call, invoke_call])

    result = await multicall.execute(calls)

    await devnet.assert_transaction_accepted(result.transaction_hash)
