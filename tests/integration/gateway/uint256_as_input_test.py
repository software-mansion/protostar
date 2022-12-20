from pathlib import Path

import pytest

from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import CONTRACT_WITH_UINT256_CONSTRUCTOR
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture
from protostar.starknet_gateway.gateway_facade import TransactionException
from protostar.starknet.data_transformer import CairoOrPythonData


@pytest.fixture(name="protostar", scope="module")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./src/main.cairo": CONTRACT_WITH_UINT256_CONSTRUCTOR})
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_filepath")
def compiled_contract_filepath_fixture() -> Path:
    return Path("./build/main.json")


@pytest.mark.parametrize(
    "constructor_input",
    [[42, 24], {"amount": {"high": 24, "low": 42}}, {"amount": (24 << 128) + 42}],
)
async def test_uint256_as_input(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    compiled_contract_filepath: Path,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    constructor_input: CairoOrPythonData,
):
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=compiled_contract_filepath,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )
        response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
            inputs=constructor_input,
        )
        assert response.address is not None

        response = await protostar.call(
            contract_address=response.address,
            function_name="get_balance",
            inputs=None,
            gateway_url=devnet_gateway_url,
        )

        assert response.call_output.cairo_data == [42, 24]


async def test_uint256_as_input_fail(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    compiled_contract_filepath: Path,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        declare_response = await protostar.declare(
            contract=compiled_contract_filepath,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
        )

        with pytest.raises(TransactionException):
            await protostar.deploy(
                class_hash=declare_response.class_hash,
                gateway_url=devnet_gateway_url,
                account_address=devnet_account.address,
                max_fee="auto",
                inputs=[(24 << 128) + 42],
            )
