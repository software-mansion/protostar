from pathlib import Path

import pytest
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from protostar.starknet_gateway.gateway_facade import (
    ContractNotFoundException,
    GatewayFacade,
    InputValidationException,
    UnknownFunctionException,
)
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR


@pytest.fixture(autouse=True, scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(protostar: ProtostarFixture) -> Path:
    return protostar.project_root_path / "build" / "main.json"


@pytest.fixture(name="gateway_facade")
def gateway_facade_fixture(devnet_gateway_url: str):
    return GatewayFacade(
        gateway_client=GatewayClient(
            net=devnet_gateway_url, chain=StarknetChainId.TESTNET
        ),
        project_root_path=Path(),
    )


async def test_deploy(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.deploy(compiled_contract_path, [42])
    assert response is not None


async def test_deploy_no_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    with pytest.raises(InputValidationException):
        await gateway_facade.deploy(compiled_contract_path, [])


@pytest.mark.skip("https://github.com/software-mansion/starknet.py/pull/323")
async def test_deploy_too_many_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    with pytest.raises(InputValidationException):
        await gateway_facade.deploy(compiled_contract_path, [42, 24])


async def test_declare(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.declare(compiled_contract_path)
    assert response is not None


async def test_call(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    initial_balance = 42
    deployed_contract = await gateway_facade.deploy(
        compiled_contract_path, [initial_balance]
    )

    response = await gateway_facade.call(
        deployed_contract.address,
        function_name="get_balance",
        inputs={},
    )

    assert response[0] == initial_balance


async def test_call_to_unknown_function(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path, [42])

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
    deployed_contract = await gateway_facade.deploy(compiled_contract_path, [42])

    with pytest.raises(InputValidationException):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="get_balance",
            inputs={"UNKNOWN_ARG": 42},
        )


async def test_call_to_with_positional_incorrect_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path, [42])

    with pytest.raises(InputValidationException):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="get_balance",
            inputs=[42],
        )
