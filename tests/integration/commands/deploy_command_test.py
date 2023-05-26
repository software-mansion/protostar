from pathlib import Path

import pytest

from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture
from protostar.starknet_gateway.gateway_facade import InputValidationException


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        protostar_project.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
        protostar_project.protostar.build_cairo0_sync()
        yield protostar_project.protostar


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
        declare_response = await protostar.declare_cairo0(
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


async def test_deploying_contract_fail(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    compiled_contract_filepath: Path,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    devnet_account: DevnetAccount,
):
    with set_private_key_env_var(devnet_account.private_key):
        with pytest.raises(InputValidationException):
            declare_response = await protostar.declare_cairo0(
                contract=compiled_contract_filepath,
                gateway_url=devnet_gateway_url,
                max_fee="auto",
                account_address=devnet_account.address,
            )
            await protostar.deploy(
                class_hash=declare_response.class_hash,
                gateway_url=devnet_gateway_url,
                inputs={"initial_balanceee": 42},
                max_fee="auto",
                account_address=devnet_account.address,
            )
