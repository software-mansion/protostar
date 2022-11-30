from pathlib import Path

import pytest
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.starknet import Selector
from protostar.starknet_gateway.multicall import (
    MulticallUseCase,
    DeployCall,
    InvokeCall,
    MulticallInput,
)
from protostar.starknet_gateway import AccountManager, GatewayFacade
from tests._conftest.devnet import DevnetFixture
from tests.conftest import SetPrivateKeyEnvVarFixture
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="starknet_client")
def gateway_facade_fixture(devnet: DevnetFixture):
    return GatewayFacade(
        gateway_client=GatewayClient(net=devnet.get_gateway_url()),
        compiled_contract_reader=CompiledContractReader(),
        project_root_path=Path(),
    )


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


async def test_multicall_use_case_happy_case(
    protostar: ProtostarFixture,
    starknet_client: GatewayFacade,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    account = devnet.get_predeployed_accounts()[0]
    account_manager = AccountManager(
        private_key=int(account.private_key, base=0),
        signer=account.signer,
        address=account.address,
        gateway_url=devnet.get_gateway_url(),
        max_fee="auto",
    )
    with set_private_key_env_var(account.private_key):
        declare_result = await protostar.declare(
            contract=Path() / "build" / "main.json",
            account_address=account.address,
            chain_id=StarknetChainId.TESTNET,
            wait_for_acceptance=True,
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
        )
        multicall = MulticallUseCase(
            account_manager=account_manager,
            client=starknet_client,
        )
        deploy_call = DeployCall(
            name="A",
            class_hash=declare_result.class_hash,
            calldata=[],
        )
        invoke_call = InvokeCall(
            address="A",
            calldata=[42],
            selector=Selector("increase_balance"),
        )
        calls = MulticallInput(calls=[deploy_call, invoke_call])

        result = await multicall.execute(calls)

        await devnet.assert_transaction_accepted(result.transaction_hash)

        contract_a_address = result.deployed_contract_addresses["A"]
        call_result = await protostar.call(
            contract_address=contract_a_address,
            function_name="get_balance",
            gateway_url=devnet.get_gateway_url(),
            inputs=[],
        )
        assert call_result.response.res == 42
