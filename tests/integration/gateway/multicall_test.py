from pathlib import Path

import pytest
from starknet_py.net.gateway_client import GatewayClient

from protostar.compiler.compiled_contract_reader import CompiledContractReader
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


@pytest.fixture(name="starknet_client")
def gateway_facade_fixture(devnet: DevnetFixture):
    return GatewayFacade(
        gateway_client=GatewayClient(net=devnet.get_gateway_url()),
        compiled_contract_reader=CompiledContractReader(),
        project_root_path=Path(),
    )


async def test_multicall_use_case_happy_case(
    starknet_client: GatewayFacade, devnet: DevnetFixture
):
    account = devnet.get_predeployed_accounts()[0]
    account_manager = AccountManager(
        private_key=int(account.private_key, base=0),
        signer=account.signer,
        address=account.address,
        gateway_url=devnet.get_gateway_url(),
        max_fee="auto",
    )
    multicall = MulticallUseCase(
        account_manager=account_manager,
        client=starknet_client,
        call_resolver=CallResolver(),
        resolved_calls_to_calldata_converter=ResolvedCallsToCalldataConverter(),
    )
    deploy_call = DeployCall(
        name="A",
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
