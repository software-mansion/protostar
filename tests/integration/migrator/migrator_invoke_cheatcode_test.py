import pytest
import requests
from starknet_py.contract import Contract
from starknet_py.net import KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starkware.crypto.signature.signature import get_random_private_key
from migrator.compiled_account_contract_tx_v0 import COMPILED_ACCOUNT_CONTRACT_TX_V0

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from protostar.starknet import Address
from tests.conftest import Credentials
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.migrator.conftest import MigrateFixture


@pytest.fixture(autouse=True, scope="module", name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
        protostar.build_sync()
        yield protostar


async def test_happy_case(
    migrate: MigrateFixture,
    signing_credentials: Credentials,
    monkeypatch: pytest.MonkeyPatch,
):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
declaration = declare("./build/main.json", config={"max_fee": "auto"})
contract_address = deploy_contract(declaration.class_hash, constructor_args=[0]).contract_address

invoke(contract_address, "increase_balance", {"amount": 42}, config={"max_fee": "auto"})

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )


async def test_waiting_for_acceptance(
    migrate: MigrateFixture,
    signing_credentials: Credentials,
    monkeypatch: pytest.MonkeyPatch,
):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
declaration = declare("./build/main.json", config={"max_fee": "auto"})
contract_address = deploy_contract(declaration.class_hash, constructor_args=[0]).contract_address

invoke(
    contract_address,
    "increase_balance",
    {"amount": 42},
    config={"wait_for_acceptance": True, "max_fee": "auto"}
)

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )
