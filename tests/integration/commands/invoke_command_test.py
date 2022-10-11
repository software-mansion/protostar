import pytest

from tests.conftest import DevnetAccount
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.migrator.conftest import assert_transaction_accepted
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


async def test_nothing(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
):
    deploy_response = await protostar.deploy(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )
    response = await protostar.invoke(
        contract_address=deploy_response.address,
        function_name="increase_balance",
        inputs=[42],
        max_fee="auto",
        account_address=devnet_account.address,
        signer=devnet_account.signer,
        wait_for_acceptance=True,
    )

    await assert_transaction_accepted(devnet_gateway_url, response.transaction_hash)
