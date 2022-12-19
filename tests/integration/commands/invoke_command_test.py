import pytest

from protostar.protostar_exception import ProtostarException
from protostar.starknet.data_transformer import CairoOrPythonData
from tests._conftest.devnet import DevnetFixture
from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import (
    RUNTIME_ERROR_CONTRACT,
    CONTRACT_WITH_UINT256_CONSTRUCTOR,
)
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


async def deploy_main_contract(
    protostar: ProtostarFixture, devnet_gateway_url: str, devnet_account: DevnetAccount
):
    declare_response = await protostar.declare(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
        account_address=devnet_account.address,
        max_fee="auto",
    )
    return await protostar.deploy(
        class_hash=declare_response.class_hash,
        gateway_url=devnet_gateway_url,
        account_address=devnet_account.address,
        max_fee="auto",
    )


async def test_invoke(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
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


@pytest.mark.parametrize("new_value", [[42, 0], {"amount": 42}])
async def test_invoke_uint256_(
    protostar: ProtostarFixture,
    devnet_account: DevnetAccount,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    new_value: CairoOrPythonData,
):
    protostar.create_files({"src/main.cairo": CONTRACT_WITH_UINT256_CONSTRUCTOR})
    await protostar.build()
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
            account_address=devnet_account.address,
            wait_for_acceptance=True,
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet.get_gateway_url(),
            max_fee="auto",
            account_address=devnet_account.address,
            inputs=[0, 0],
            wait_for_acceptance=True,
        )

        await protostar.invoke(
            contract_address=deploy_response.address,
            function_name="set_balance",
            inputs=new_value,
            max_fee="auto",
            account_address=devnet_account.address,
            wait_for_acceptance=True,
            gateway_url=devnet.get_gateway_url(),
        )

    result = await protostar.call(
        contract_address=deploy_response.address,
        function_name="get_balance",
        gateway_url=devnet.get_gateway_url(),
        inputs=[],
    )

    assert result.call_output.cairo_data == [42, 0]
    assert result.call_output.human_data is not None
    assert result.call_output.human_data["res"] == 42


async def test_invoke_args_dict(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    devnet: DevnetFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar, devnet_gateway_url, devnet_account
        )
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
    with set_private_key_env_var(devnet_account.private_key):
        deploy_response = await deploy_main_contract(
            protostar, devnet_gateway_url, devnet_account
        )
        with pytest.raises(ProtostarException):
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
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
        )
        deploy_response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
            account_address=devnet_account.address,
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
