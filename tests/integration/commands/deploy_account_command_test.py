import pytest

from tests._conftest.devnet import DevnetFixture
from tests.conftest import SetPrivateKeyEnvVarFixture
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_deploying_account(
    protostar: ProtostarFixture,
    devnet: DevnetFixture,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
):
    salt = 1
    account = await devnet.prepare_account(private_key=int("0x123", base=16), salt=salt)
    with set_private_key_env_var("0x123"):

        response = await protostar.deploy_account(
            account_address=account.address,
            account_address_salt=salt,
            account_class_hash=account.class_hash,
            account_constructor_input=[int(account.public_key)],
            max_fee=int(1e16),
            nonce=0,
            gateway_url=devnet.get_gateway_url(),
        )

        tx = protostar.get_intercepted_transactions_mapping().deploy_account_txs[0]
        assert tx.class_hash == account.class_hash
        assert tx.contract_address_salt == salt
        await devnet.assert_transaction_accepted(response.transaction_hash)
