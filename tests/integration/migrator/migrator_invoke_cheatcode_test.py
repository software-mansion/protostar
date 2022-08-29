import pytest

from protostar.cli.signable_command_util import PRIVATE_KEY_ENV_VAR_NAME
from tests.data.contracts import CONTRACT_WITH_CONSTRUCTOR
from tests.integration.migrator.conftest import MigrateFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True, scope="module")
def setup(protostar: ProtostarFixture):
    protostar.init_sync()
    protostar.create_files({"./src/main.cairo": CONTRACT_WITH_CONSTRUCTOR})
    protostar.build_sync()


async def test_happy_case(migrate: MigrateFixture, signing_credentials, monkeypatch):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
contract_address = deploy_contract("./build/main.json", constructor_args=[0]).contract_address

invoke(contract_address, "increase_balance", {"amount": 42}, auto_estimate_fee=True)

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )


async def test_waiting_for_pending(
    migrate: MigrateFixture, signing_credentials, monkeypatch
):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
contract_address = deploy_contract("./build/main.json", constructor_args=[0]).contract_address

invocation = invoke(contract_address, "increase_balance", {"amount": 42}, auto_estimate_fee=True)

invocation.wait_for_acceptance()

assert invocation.status == "PENDING"

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )


async def test_waiting_for_acceptance(
    migrate: MigrateFixture, signing_credentials, monkeypatch
):
    private_key, acc_address = signing_credentials
    monkeypatch.setenv(PRIVATE_KEY_ENV_VAR_NAME, private_key)

    await migrate(
        """
contract_address = deploy_contract("./build/main.json", constructor_args=[0]).contract_address

invocation = invoke(contract_address, "increase_balance", {"amount": 42}, auto_estimate_fee=True)

invocation.wait_for_acceptance()

assert invocation.status == "ACCEPTED_ON_L2"

result = call(contract_address, "get_balance")

assert result.res == 42
""",
        account_address=acc_address,
    )
