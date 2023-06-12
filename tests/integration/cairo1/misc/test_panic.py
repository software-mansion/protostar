from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarProjectFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar_project", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        yield protostar_project


async def test_panic(protostar_project: ProtostarProjectFixture, datadir: Path):
    testing_summary = await protostar_project.protostar.test(
        datadir / "panic_test.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_failed_test_cases_names=["test_panic"],
    )
