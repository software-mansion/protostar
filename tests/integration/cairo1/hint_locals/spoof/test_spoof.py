from pathlib import Path

import pytest

from protostar.cairo import CairoVersion
from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar_project", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(CairoVersion.cairo1) as protostar_project:
        yield protostar_project


async def test_spoof_hint_local(
    protostar_project: ProtostarProjectFixture, shared_datadir: Path
):
    protostar_project.create_contracts_cairo1(
        {
            "simple": shared_datadir / "simple",
            "proxy": shared_datadir / "proxy",
        }
    )
    protostar_project.create_contracts_cairo1({})

    testing_summary = await protostar_project.protostar.test(
        Path(__file__).parent / "spoof_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_start_spoof_transaction_hash_doesnt_affect_other_fields",
            "test_spoof_tx_info",
            "test_start_stop_spoof_max_fee",
            "test_stop_spoof_on_non_existent",
            "test_stop_spoof_on_not_spoofed",
            "test_stop_spoof_multiple_times",
            "test_start_spoof_latest_takes_precedence",
            "test_stop_spoof_cancels_all_spoofs",
            "test_spoof_multiple_times",
            "test_spoof_behind_proxy",
        ],
    )
