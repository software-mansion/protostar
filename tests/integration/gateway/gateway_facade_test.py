from pathlib import Path
from typing import cast

import pytest
from starknet_py.net.client_models import Declare, TransactionStatus
from starknet_py.net.gateway_client import GatewayClient

from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.starknet import Address
from protostar.starknet_gateway import (
    ContractNotFoundException,
    DeployAccountArgs,
    FeeExceededMaxFeeException,
    GatewayFacade,
    InputValidationException,
    UnknownFunctionException,
)
from tests._conftest.devnet import DevnetAccount, DevnetFixture
from tests.conftest import MAX_FEE, TESTS_ROOT_PATH
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR, IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import (
    GatewayClientTxInterceptor,
    ProtostarFixture,
    TransactionRegistry,
)


@pytest.fixture(autouse=True, scope="function", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(protostar: ProtostarFixture) -> Path:
    return protostar.project_root_path / "build" / "main.json"


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
        compiled_contract_reader=CompiledContractReader(),
        project_root_path=Path(),
    )


async def test_deploy(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.deploy(compiled_contract_path)
    assert response is not None


async def test_declare(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.declare_v0(compiled_contract_path)
    assert response is not None


async def test_call(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    response = await gateway_facade.call(
        deployed_contract.address,
        function_name="get_balance",
        inputs={},
    )

    initial_balance = 0
    assert response[0] == initial_balance


async def test_call_to_unknown_function(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    with pytest.raises(UnknownFunctionException):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="UNKNOWN_FUNCTION",
            inputs={},
        )


async def test_call_to_unknown_contract(gateway_facade: GatewayFacade):
    with pytest.raises(ContractNotFoundException):
        await gateway_facade.call(
            Address.from_user_input(123),
            function_name="UNKNOWN_FUNCTION",
        )


async def test_call_to_with_incorrect_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    with pytest.raises(InputValidationException):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="get_balance",
            inputs={"UNKNOWN_ARG": 42},
        )


async def test_call_to_with_positional_incorrect_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    with pytest.raises(InputValidationException):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="get_balance",
            inputs=[42],
        )


@pytest.fixture(name="compiled_contract_without_constructor_path")
def compiled_contract_without_constructor_path_fixture(protostar: ProtostarFixture):
    protostar.create_files({"./src/main.cairo": IDENTITY_CONTRACT})
    protostar.build_sync()
    yield protostar.project_root_path / "build" / "main.json"


async def test_deploy_fail_input_without_constructor(
    gateway_facade: GatewayFacade, compiled_contract_without_constructor_path: Path
):
    with pytest.raises(InputValidationException) as ex:
        await gateway_facade.deploy(
            compiled_contract_without_constructor_path, inputs={"UNKNOWN_INPUT": 42}
        )
    assert "Inputs provided to a contract with no constructor." in str(ex.value)


@pytest.fixture(name="compiled_contract_with_contractor_path")
def compiled_contract_with_contractor_path_fixture(protostar: ProtostarFixture):
    protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
    protostar.build_sync()
    yield protostar.project_root_path / "build" / "main.json"


@pytest.mark.parametrize("inputs", [[42], {"initial_balance": 42}])
async def test_deploy_supports_data_transformer(
    gateway_facade: GatewayFacade,
    compiled_contract_with_contractor_path: Path,
    inputs: CairoOrPythonData,
):
    await gateway_facade.deploy(compiled_contract_with_contractor_path, inputs=inputs)


async def test_deploy_no_args(
    gateway_facade: GatewayFacade, compiled_contract_with_contractor_path: Path
):
    with pytest.raises(InputValidationException):
        await gateway_facade.deploy(compiled_contract_with_contractor_path)


@pytest.mark.skip("https://github.com/software-mansion/starknet.py/pull/323")
async def test_deploy_too_many_args(
    gateway_facade: GatewayFacade, compiled_contract_with_contractor_path: Path
):
    with pytest.raises(InputValidationException):
        await gateway_facade.deploy(compiled_contract_with_contractor_path, [42, 24])


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


async def test_calling_through_proxy(
    gateway_facade: GatewayFacade,
    compiled_contract_path: Path,
):
    contract = await gateway_facade.deploy(
        compiled_contract_path=compiled_contract_path, wait_for_acceptance=True, salt=2
    )
    proxy = await gateway_facade.deploy(
        compiled_contract_path=TESTS_ROOT_PATH
        / "data"
        / "oz_proxy_compiled_contract.json",
        inputs=[int(contract.address)],
        wait_for_acceptance=True,
    )

    call_result = await gateway_facade.call(
        address=proxy.address,
        function_name="get_balance",
    )

    assert call_result.res == 0  # type: ignore
