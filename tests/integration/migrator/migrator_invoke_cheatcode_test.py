import pytest
import requests
from starknet_py.contract import Contract
from starknet_py.net import KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starkware.crypto.signature.signature import get_random_private_key

from migrator.compiled_account_contract_tx_v0 import COMPILED_ACCOUNT_CONTRACT_TX_V0
from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
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
    migrate: MigrateFixture, signing_credentials, monkeypatch: pytest.MonkeyPatch
):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
contract_address = deploy_contract("./build/main.json", constructor_args=[0]).contract_address

invoke(contract_address, "increase_balance", {"amount": 42}, config={"auto_estimate_fee": True})

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )


async def test_waiting_for_acceptance(
    migrate: MigrateFixture, signing_credentials, monkeypatch: pytest.MonkeyPatch
):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
contract_address = deploy_contract("./build/main.json", constructor_args=[0]).contract_address

invoke(
    contract_address,
    "increase_balance",
    {"amount": 42},
    config={"auto_estimate_fee": True, "wait_for_acceptance": True}
)

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )


async def test_account_with_tx_version_0(
    devnet_gateway_url: str, migrate: MigrateFixture, monkeypatch: pytest.MonkeyPatch
):
    # TODO(mkaput): Remove this when Cairo 0.11 will remove transactions v0.

    gateway_client = GatewayClient(devnet_gateway_url)

    key_pair = KeyPair.from_private_key(get_random_private_key())
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, hex(key_pair.private_key))

    deployment_result = await Contract.deploy(
        client=gateway_client,
        compiled_contract=COMPILED_ACCOUNT_CONTRACT_TX_V0,
        constructor_args=[key_pair.public_key],
    )
    await deployment_result.wait_for_acceptance()

    account_address = hex(deployment_result.deployed_contract.address)

    requests.post(
        f"{devnet_gateway_url}/mint",
        json={
            "address": account_address,
            "amount": 1e21,
            "lite": True,
        },
    )

    await migrate(
        """
contract_address = deploy_contract("./build/main.json", constructor_args=[0]).contract_address

# Call 2 times to check caching works.
invoke(contract_address, "increase_balance", {"amount": 20}, config={"auto_estimate_fee": True})

invoke(contract_address, "increase_balance", {"amount": 22}, config={"auto_estimate_fee": True})

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=account_address,
    )
