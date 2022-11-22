from cairo_rs_py import CairoRunner  # type: ignore
from pathlib import Path

import pytest

from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture
from tests.data.contracts import SIMPLE_CONTRACT
from tests.integration.conftest import (
    RunCairoTestRunnerFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar", scope="module")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with open(str(Path(__file__).parent / "cairo_rs_test.cairo")) as file:
        with create_protostar_project() as protostar:
            protostar.create_files({"./src/main.cairo": SIMPLE_CONTRACT})
            protostar.build_sync()
            yield protostar


@pytest.fixture(name="compiled_contract_filepath")
def compiled_contract_filepath_fixture() -> Path:
    return Path("./build/main.json")


def test_cairo_rs_from_json(
    protostar: ProtostarFixture, compiled_contract_filepath: Path
):
    with open(compiled_contract_filepath) as file:
        CairoRunner(file.read(), "main", "all", False).cairo_run(False)


@pytest.mark.asyncio
async def test_cairo_rs_from_file(
    run_cairo_test_runner: RunCairoTestRunnerFixture,
):
    testing_summary = await run_cairo_test_runner(
        Path(__file__).parent / "cairo_rs_test.cairo"
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_basic",
        ],
    )
