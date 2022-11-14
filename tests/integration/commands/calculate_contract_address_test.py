import pytest

from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_calculate_contract_address(protostar: ProtostarFixture):
    account_address = await protostar.calculate_account_address(
        account_address_salt=1, account_class_hash=1, account_constructor_input=[1]
    )

    assert (
        account_address
        == "0x02eb86e468001ec76336865ff416dfc32ba7b002afd3c65b500b9642e1a679fc"
    )
