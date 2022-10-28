import pytest

from tests._conftest.devnet import DevnetFixture
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_deploying_account(protostar: ProtostarFixture, devnet: DevnetFixture):
    salt = 1
    account = await devnet.prepare_account(private_key=123, salt=salt)

    response = await protostar.deploy_account(
        account_address=account.address,
        account_address_salt=salt,
        account_class_hash=account.class_hash,
        account_constructor_input=[int(account.public_key)],
        max_fee=1e16,
        signer=account.signer,
        nonce=0,
    )
    tx = protostar.get_intercepted_transactions_mapping().deploy_account_txs[0]

    assert tx.class_hash == account.class_hash
    assert tx.contract_address_salt == salt
    await devnet.assert_transaction_accepted(response.transaction_hash)
