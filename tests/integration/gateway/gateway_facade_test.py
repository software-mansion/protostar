from pathlib import Path
from typing import Optional

import pytest
from starknet_py.net.client_models import StarknetTransaction, TransactionStatus
from starknet_py.net.gateway_client import GatewayClient, Network
from starkware.starknet.services.api.gateway.transaction import Declare

from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.starknet_gateway.gateway_facade import (
    ContractNotFoundException,
    GatewayFacade,
    InputValidationException,
    UnknownFunctionException,
)
from protostar.utils.data_transformer import CairoOrPythonData
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR, IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture, DevnetAccount
from tests.integration.protostar_fixture import ProtostarFixture


class GatewayClientTxInterceptor(GatewayClient):
    def __init__(self, net: Network):
        super().__init__(net, session=None)
        self.intercepted_txs: list[StarknetTransaction] = []

    async def _add_transaction(
        self,
        tx: StarknetTransaction,
        token: Optional[str] = None,
    ) -> dict:
        self.intercepted_txs.append(tx)
        return await super()._add_transaction(tx, token)


@pytest.fixture(autouse=True, scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(protostar: ProtostarFixture) -> Path:
    return protostar.project_root_path / "build" / "main.json"


@pytest.fixture(name="gateway_client")
def gateway_client_fixture(devnet_gateway_url: str):
    return GatewayClientTxInterceptor(devnet_gateway_url)


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
            123,
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
    protostar.init_sync()
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
    protostar.init_sync()
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
    )

    assert result.code == TransactionStatus.ACCEPTED_ON_L2
    assert len(gateway_client.intercepted_txs) == 1
    declare_tx = gateway_client.intercepted_txs[0]
    assert isinstance(declare_tx, Declare)
    assert declare_tx.signature
