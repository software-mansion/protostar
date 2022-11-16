from pathlib import Path

import pytest
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from protostar.starknet.account_address import AccountAddress
from protostar.starknet_gateway import FeeExceededMaxFeeException
from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar", scope="module")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
        protostar.build_sync()
        yield protostar


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture() -> Path:
    return Path("./build/main.json")


async def test_declaring_contract(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    compiled_contract_path: Path,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        response = await protostar.declare(
            chain_id=StarknetChainId.TESTNET,
            account_address=devnet_account.address,
            contract=compiled_contract_path,
            gateway_url=devnet_gateway_url,
            max_fee="auto",
        )

        assert response.class_hash is not None


async def test_max_fee_is_respected(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    compiled_contract_path: Path,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    with set_private_key_env_var(devnet_account.private_key):
        with pytest.raises(FeeExceededMaxFeeException):
            await protostar.declare(
                chain_id=StarknetChainId.TESTNET,
                account_address=devnet_account.address,
                contract=compiled_contract_path,
                gateway_url=devnet_gateway_url,
                max_fee=1,
                wait_for_acceptance=True,
            )


@pytest.mark.xfail(
    reason="This test is going to fail since sending signed deploy txs is supported only for devnet, and now it's "
    "disabled "
)
async def test_deploying_contract_with_signing(
    devnet_gateway_url: str,
    protostar: ProtostarFixture,
    compiled_contract_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, "123")

    response = await protostar.declare(
        chain_id=StarknetChainId.TESTNET,
        account_address=AccountAddress.from_user_input("123"),
        contract=compiled_contract_path,
        gateway_url=devnet_gateway_url,
        wait_for_acceptance=True,
    )

    assert response.class_hash is not None

    gateway_client = GatewayClient(devnet_gateway_url)
    transaction = await gateway_client.get_transaction(response.transaction_hash)
    assert transaction.signature == [
        "3459263272550625393812584460277149848351409720716906360199187355059506361232",
        "1830633873577487268914590325347030490499699872026627682646826922183589844384",
    ]


def test_account_doesnt_exist():
    pass  # TODO: Implement in 0.10
