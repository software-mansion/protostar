from typing import Union

import pytest
from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient

from protostar.protostar_exception import ProtostarException
from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import RUNTIME_ERROR_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


async def assert_transaction_accepted(
    devnet_gateway_url: str, transaction_hash: Union[str, int]
):
    gateway = GatewayClient(devnet_gateway_url)
    (_, transaction_status) = await gateway.wait_for_tx(
        transaction_hash, wait_for_accept=True
    )
    assert transaction_status == TransactionStatus.ACCEPTED_ON_L2


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


async def test_invoke(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    declare_response = await protostar.declare(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )
    deploy_response = await protostar.deploy(
        declare_response.class_hash,
        gateway_url=devnet_gateway_url,
    )

    with set_private_key_env_var(devnet_account.private_key):
        response = await protostar.invoke(
            contract_address=deploy_response.address,
            function_name="increase_balance",
            inputs=[42],
            max_fee="auto",
            account_address=devnet_account.address,
            wait_for_acceptance=True,
            gateway_url=devnet_gateway_url,
        )

        await assert_transaction_accepted(devnet_gateway_url, response.transaction_hash)
    # The one at 0 is actually a UDC Invoke, for deploy
    transaction = protostar.get_intercepted_transactions_mapping().invoke_txs[1]
    assert transaction.max_fee != "auto"
    assert transaction.calldata[6] == 42
    assert transaction.version == 1


async def test_handling_invoke_failure(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    protostar.create_files({"./src/main.cairo": RUNTIME_ERROR_CONTRACT})
    await protostar.build()
    declare_response = await protostar.declare(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )
    deploy_response = await protostar.deploy(
        declare_response.class_hash,
        gateway_url=devnet_gateway_url,
    )

    with pytest.raises(ProtostarException, match="1 != 0"):
        with set_private_key_env_var(devnet_account.private_key):
            await protostar.invoke(
                contract_address=deploy_response.address,
                function_name="fail",
                inputs=[],
                max_fee="auto",
                account_address=devnet_account.address,
                wait_for_acceptance=True,
                gateway_url=devnet_gateway_url,
            )
