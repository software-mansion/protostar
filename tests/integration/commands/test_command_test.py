from pathlib import Path

from tests.integration.conftest import ProtostarFixture


async def test_gas_estimation(
    protostar: ProtostarFixture, devnet_fixture: DevnetFixture, datadir: Path
):
    await protostar.build()

    devnet_fixture.get_gas_price()
    testing_result = await protostar.test(targets=["tests"], gas_price=1)

    assert testing_result.passed[0].execution_resources.estimated_fee == SNAPSHOT_VALUE
