from typing import Union

import pytest

from protostar.protostar_exception import ProtostarException
from tests._conftest.devnet import DevnetFixture
from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import RUNTIME_ERROR_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture

from protostar.starknet_gateway.gateway_facade import InputValidationException


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


async def deploy_main_contract(protostar: ProtostarFixture, devnet_gateway_url: str):
    declare_response = await protostar.declare(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )
    return await protostar.deploy(
        class_hash=declare_response.class_hash,
        gateway_url=devnet_gateway_url,
    )


async def test_invoke(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    declare_response = await protostar.declare(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )
    deploy_response = await protostar.deploy(
        class_hash=declare_response.class_hash,
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
        await devnet.assert_transaction_accepted(response.transaction_hash)
    # The one at 0 is actually a UDC Invoke, for deploy
    transaction = protostar.get_intercepted_transactions_mapping().invoke_txs[1]
    assert transaction.max_fee != "auto"
    assert transaction.calldata[6] == 42
    assert transaction.version == 1


async def test_invoke_args_dict(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    devnet: DevnetFixture,
):
    deploy_response = await deploy_main_contract(protostar, devnet_gateway_url)

    with set_private_key_env_var(devnet_account.private_key):
        response = await protostar.invoke(
            contract_address=deploy_response.address,
            function_name="increase_balance",
            inputs={"amount": 42},
            max_fee="auto",
            account_address=devnet_account.address,
            wait_for_acceptance=True,
            gateway_url=devnet_gateway_url,
        )
        await devnet.assert_transaction_accepted(response.transaction_hash)


async def test_invoke_args_dict_fail(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    deploy_response = await deploy_main_contract(protostar, devnet_gateway_url)

    with set_private_key_env_var(devnet_account.private_key):
        with pytest.raises(InputValidationException):
            await protostar.invoke(
                contract_address=deploy_response.address,
                function_name="increase_balance",
                inputs={"amounttt": 42},
                max_fee="auto",
                account_address=devnet_account.address,
                wait_for_acceptance=True,
                gateway_url=devnet_gateway_url,
            )


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
        class_hash=declare_response.class_hash,
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
