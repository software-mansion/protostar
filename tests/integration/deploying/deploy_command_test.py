from pathlib import Path

import pytest

from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture

from protostar.starknet_gateway.gateway_facade import InputValidationException


@pytest.fixture(name="protostar", scope="module")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_filepath")
def compiled_contract_filepath_fixture() -> Path:
    return Path("./build/main.json")


async def test_deploying_contract(
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
        response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            account_address=devnet_account.address,
            max_fee="auto",
            inputs=[42],
        )
    assert response.address is not None


async def test_deploying_contract_arg_dict(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    compiled_contract_filepath: Path,
):
    declare_response = await protostar.declare(
        contract=compiled_contract_filepath,
        gateway_url=devnet_gateway_url,
    )
    with pytest.raises(InputValidationException):
        response = await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            inputs={"initial_balance": 42},
        )


async def test_deploying_contract_fail(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    compiled_contract_filepath: Path,
):
    with pytest.raises(InputValidationException):
        declare_response = await protostar.declare(
            contract=compiled_contract_filepath,
            gateway_url=devnet_gateway_url,
        )
        await protostar.deploy(
            class_hash=declare_response.class_hash,
            gateway_url=devnet_gateway_url,
            inputs={"initial_balanceee": 42},
        )
