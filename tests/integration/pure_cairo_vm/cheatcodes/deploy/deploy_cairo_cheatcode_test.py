from pathlib import Path

import pytest

from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)
from tests.integration._conftest import ProtostarFixture
from tests.integration.pure_cairo_vm.conftest import (
    CONTRACTS_PATH,
)

TEST_PATH = Path(__file__).parent


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_deploy_pipeline(protostar: ProtostarFixture):
    protostar.create_files(
        {
            "basic": CONTRACTS_PATH / "basic_contract.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        TEST_PATH / "deploy_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_deploying_pipeline",
            "test_deploying_pipeline_with_path",
            "test_two_interleaving_flows",
        ],
    )
