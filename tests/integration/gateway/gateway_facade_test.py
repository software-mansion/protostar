from pathlib import Path

import pytest
from starknet_py.net.gateway_client import GatewayClient

from protostar.compiler.compiled_contract_reader import CompiledContractReader
from protostar.starknet_gateway.gateway_facade import (
    ContractNotFoundException,
    GatewayFacade,
    InputValidationException,
    UnknownFunctionException,
)
from protostar.utils.data_transformer import CairoOrPythonData
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR, IDENTITY_CONTRACT
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True, scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(protostar: ProtostarFixture) -> Path:
    return protostar.project_root_path / "build" / "main.json"


@pytest.fixture(name="gateway_facade")
def gateway_facade_fixture(devnet_gateway_url: str):
    return GatewayFacade(
        gateway_client=GatewayClient(devnet_gateway_url),
        compiled_contract_reader=CompiledContractReader(),
        project_root_path=Path(),
    )


async def test_deploy(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.deploy(compiled_contract_path)
    assert response is not None


async def test_declare(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.declare(compiled_contract_path)
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
