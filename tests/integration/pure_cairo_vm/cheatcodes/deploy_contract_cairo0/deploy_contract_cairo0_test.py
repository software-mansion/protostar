from pathlib import Path

import pytest

from protostar.cairo import CairoVersion
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.cheatcodes.conftest import CONTRACTS_TEMPLATES_PATH


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project(cairo_version=CairoVersion.cairo1) as protostar:
        yield protostar


async def test_deploy_contract_cairo0(protostar: ProtostarFixture):
    # TODO(pmagiera)
    protostar.create_contracts(
        {
            "basic_contract_cairo0": CONTRACTS_TEMPLATES_PATH / "basic_contract.cairo",
            "broken_syntax_contract": CONTRACTS_TEMPLATES_PATH
            / "broken_syntax_contract.cairo",
        },
    )

    testing_summary = await protostar.run_test_runner(
        Path(__file__).parent / "deploy_contract_cairo0_test.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[],
        expected_failed_test_cases_names=[],
    )
