from pathlib import Path
from typing import cast

import pytest
from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models.transaction import Declare

from protostar.protostar_exception import ProtostarException
from protostar.starknet.contract_abi import ContractAbi
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet import Address, Selector
from protostar.starknet_gateway import (
    DeployAccountArgs,
    FeeExceededMaxFeeException,
    GatewayFacade,
    InputValidationException,
)
from tests._conftest.devnet import DevnetAccount, DevnetFixture
from tests.conftest import MAX_FEE, SetPrivateKeyEnvVarFixture
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR, IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import (
    GatewayClientTxInterceptor,
    TransactionRegistry,
    ProtostarProjectFixture,
)


@pytest.fixture(autouse=True, scope="function", name="protostar_project")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        protostar_project.protostar.build_cairo0_sync()
        yield protostar_project


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(protostar_project: ProtostarProjectFixture) -> Path:
    return protostar_project.project_root_path / "build" / "main.json"


@pytest.fixture(name="transaction_registry")
def transaction_registry_fixture() -> TransactionRegistry:
    return TransactionRegistry()


@pytest.fixture(name="gateway_client")
def gateway_client_fixture(
    devnet_gateway_url: str, transaction_registry: TransactionRegistry
):
    return GatewayClientTxInterceptor(
        devnet_gateway_url, transaction_registry=transaction_registry
    )


@pytest.fixture(name="gateway_facade")
def gateway_facade_fixture(gateway_client: GatewayClient):
    return GatewayFacade(
        gateway_client=gateway_client,
        project_root_path=Path(),
    )


@pytest.fixture(name="declared_class_hash")
async def declared_class_hash_fixture(
    gateway_facade: GatewayFacade,
    compiled_contract_path: Path,
    devnet_account: DevnetAccount,
):
    response = await gateway_facade.declare(
        compiled_contract_path,
        signer=devnet_account.signer,
        account_address=devnet_account.address,
        max_fee="auto",
    )
    return response.class_hash


@pytest.fixture(name="contract_abi")
def contract_abi_fixture(protostar_project: ProtostarProjectFixture):
    return ContractAbi.from_json_file(
        protostar_project.project_root_path / "build" / "main_abi.json"
    )


async def test_deploy(
    gateway_facade: GatewayFacade,
    declared_class_hash: int,
    devnet_account: DevnetAccount,
):
    response = await gateway_facade.deploy_via_udc(
        declared_class_hash,
        account_address=devnet_account.address,
        signer=devnet_account.signer,
        max_fee="auto",
    )
    assert response is not None


async def test_declare(
    gateway_facade: GatewayFacade,
    compiled_contract_path: Path,
    devnet_account: DevnetAccount,
):
    response = await gateway_facade.declare(
        compiled_contract_path,
        account_address=devnet_account.address,
        signer=devnet_account.signer,
        max_fee="auto",
    )
    assert response is not None


async def test_call(
    gateway_facade: GatewayFacade,
    declared_class_hash: int,
    devnet_account: DevnetAccount,
):
    deployed_contract = await gateway_facade.deploy_via_udc(
        declared_class_hash,
        account_address=devnet_account.address,
        signer=devnet_account.signer,
        max_fee="auto",
    )

    response = await gateway_facade.send_call(
        address=deployed_contract.address,
        selector=Selector("get_balance"),
        cairo_calldata=[],
    )

    initial_balance = 0
    assert response[0] == initial_balance


async def test_call_to_unknown_function(
    gateway_facade: GatewayFacade,
    declared_class_hash: int,
    devnet_account: DevnetAccount,
):
    deployed_contract = await gateway_facade.deploy_via_udc(
        declared_class_hash,
        account_address=devnet_account.address,
        signer=devnet_account.signer,
        max_fee="auto",
    )

    with pytest.raises(
        ProtostarException,
        match='"UNKNOWN_FUNCTION" not found',
    ):
        await gateway_facade.send_call(
            address=deployed_contract.address,
            selector=Selector("UNKNOWN_FUNCTION"),
        )


async def test_call_to_unknown_contract(gateway_facade: GatewayFacade):
    with pytest.raises(
        ProtostarException,
        match="Contract .* not found",
    ):
        await gateway_facade.send_call(
            address=Address.from_user_input(123),
            selector=Selector("_"),
        )


@pytest.fixture(name="compiled_contract_without_constructor_class_hash")
async def compiled_contract_without_constructor_class_hash_fixture(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    protostar_project.create_files({"./src/main.cairo": IDENTITY_CONTRACT})
    await protostar_project.protostar.build_cairo0()
    with set_private_key_env_var(devnet_account.private_key):
        declare_res = await protostar_project.protostar.declare(
            protostar_project.protostar.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
    return declare_res.class_hash


async def test_compiled_contract_without_constructor_class_hash(
    gateway_facade: GatewayFacade,
    compiled_contract_without_constructor_class_hash: int,
    contract_abi: ContractAbi,
    devnet_account: DevnetAccount,
):
    with pytest.raises(InputValidationException) as ex:
        await gateway_facade.deploy_via_udc(
            class_hash=compiled_contract_without_constructor_class_hash,
            contract_abi=contract_abi,
            inputs={"UNKNOWN_INPUT": 42},
            account_address=devnet_account.address,
            signer=devnet_account.signer,
            max_fee="auto",
            wait_for_acceptance=True,
        )
    assert "Inputs provided to a contract with no constructor." in str(ex.value)


@pytest.fixture(name="compiled_contract_with_constructor_class_hash")
async def compiled_contract_with_constructor_class_hash_fixture(
    protostar_project: ProtostarProjectFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    protostar_project.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
    await protostar_project.protostar.build_cairo0()
    with set_private_key_env_var(devnet_account.private_key):
        declare_res = await protostar_project.protostar.declare(
            protostar_project.project_root_path / "build" / "main.json",
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
    return declare_res.class_hash


@pytest.mark.parametrize("inputs", [[42], {"initial_balance": 42}])
async def test_deploy_supports_data_transformer(
    gateway_facade: GatewayFacade,
    compiled_contract_with_constructor_class_hash: int,
    inputs: CairoOrPythonData,
    devnet_account: DevnetAccount,
    contract_abi: ContractAbi,
):
    await gateway_facade.deploy_via_udc(
        class_hash=compiled_contract_with_constructor_class_hash,
        contract_abi=contract_abi,
        inputs=inputs,
        account_address=devnet_account.address,
        signer=devnet_account.signer,
        max_fee="auto",
    )


async def test_deploy_no_args(
    gateway_facade: GatewayFacade,
    compiled_contract_with_constructor_class_hash: int,
    contract_abi: ContractAbi,
    devnet_account: DevnetAccount,
):
    with pytest.raises(InputValidationException):
        await gateway_facade.deploy_via_udc(
            compiled_contract_with_constructor_class_hash,
            contract_abi=contract_abi,
            account_address=devnet_account.address,
            signer=devnet_account.signer,
            max_fee="auto",
        )


@pytest.mark.skip("https://github.com/software-mansion/starknet.py/pull/323")
async def test_deploy_too_many_args(
    gateway_facade: GatewayFacade,
    compiled_contract_with_constructor_class_hash: int,
    devnet_account: DevnetAccount,
):
    with pytest.raises(InputValidationException):
        await gateway_facade.deploy_via_udc(
            class_hash=compiled_contract_with_constructor_class_hash,
            inputs=[42, 24],
            account_address=devnet_account.address,
            signer=devnet_account.signer,
            max_fee="auto",
        )


async def test_declare_tx_v1(
    gateway_client: GatewayClientTxInterceptor,
    gateway_facade: GatewayFacade,
    compiled_contract_path: Path,
    devnet_accounts: list[DevnetAccount],
):
    result = await gateway_facade.declare(
        compiled_contract_path=compiled_contract_path,
        account_address=devnet_accounts[0].address,
        signer=devnet_accounts[0].signer,
        wait_for_acceptance=True,
        token=None,
        max_fee=213700000000000,
    )

    assert result.code == TransactionStatus.ACCEPTED_ON_L2.value
    assert len(gateway_client.intercepted_txs) == 1
    declare_tx = gateway_client.intercepted_txs[0]
    assert isinstance(declare_tx, Declare)
    assert declare_tx.signature
    assert declare_tx.max_fee == 213700000000000


async def test_fee_exceeded_max_fee(
    gateway_facade: GatewayFacade,
    compiled_contract_path: Path,
    devnet_accounts: list[DevnetAccount],
):
    too_small_max_fee = 1

    with pytest.raises(FeeExceededMaxFeeException):
        await gateway_facade.declare(
            compiled_contract_path=compiled_contract_path,
            account_address=devnet_accounts[0].address,
            signer=devnet_accounts[0].signer,
            wait_for_acceptance=True,
            token=None,
            max_fee=too_small_max_fee,
        )


async def test_max_fee_estimation(
    gateway_facade: GatewayFacade,
    gateway_client: GatewayClientTxInterceptor,
    compiled_contract_path: Path,
    devnet_accounts: list[DevnetAccount],
):
    await gateway_facade.declare(
        compiled_contract_path=compiled_contract_path,
        account_address=devnet_accounts[0].address,
        signer=devnet_accounts[0].signer,
        wait_for_acceptance=True,
        token=None,
        max_fee="auto",
    )

    tx = cast(Declare, gateway_client.intercepted_txs[0])
    assert tx is not None
    assert tx.max_fee is not None
    assert tx.max_fee != "auto"
    assert tx.max_fee > 0


async def test_deploy_account(
    devnet: DevnetFixture,
    gateway_facade: GatewayFacade,
    transaction_registry: TransactionRegistry,
):
    salt = 1
    account = await devnet.prepare_account(salt=salt, private_key=123)
    deploy_account_args = DeployAccountArgs(
        account_address=account.address,
        account_address_salt=salt,
        account_class_hash=account.class_hash,
        account_constructor_input=[int(account.public_key)],
        max_fee=MAX_FEE,
        signer=account.signer,
        nonce=0,
    )

    response = await gateway_facade.deploy_account(deploy_account_args)

    tx = transaction_registry.deploy_account_txs[0]
    assert tx.class_hash == deploy_account_args.account_class_hash
    assert tx.contract_address_salt == deploy_account_args.account_address_salt
    await devnet.assert_transaction_accepted(response.transaction_hash)
