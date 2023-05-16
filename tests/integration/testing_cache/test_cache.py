import pytest

from protostar.self.cache_io import CacheIO
from protostar.protostar_exception import ProtostarException
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration._conftest import ProtostarFixture
from tests.data.tests import (
    TEST_BROKEN,
    TEST_FAILING,
    TEST_PARTIALLY_PASSING,
    TEST_PASSING,
)


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        protostar_project.create_files(
            {
                "./tests/test_passing.cairo": TEST_PASSING,
                "./tests/test_partially_passing.cairo": TEST_PARTIALLY_PASSING,
                "./tests/test_failing.cairo": TEST_FAILING,
                "./tests/test_broken.cairo": TEST_BROKEN,
            }
        )
        protostar_project.protostar.build_cairo0_sync()
        yield protostar_project.protostar


async def test_execute_all_tests(
    protostar: ProtostarFixture,
):
    try:
        await protostar.test_cairo0(
            [
                "./tests/test_passing.cairo",
                "./tests/test_partially_passing.cairo",
                "./tests/test_failing.cairo",
                "./tests/test_broken.cairo",
            ],
            last_failed=True,
        )
    except ProtostarException as e:
        assert str(e) == "Not all test cases passed"

    expected_tests_results = {
        "targets": [
            ("tests/test_failing.cairo", "test_fail1"),
            ("tests/test_partially_passing.cairo", "test_fail1"),
            ("tests/test_failing.cairo", "test_fail2"),
            ("tests/test_partially_passing.cairo", "test_fail2"),
            ("tests/test_broken.cairo", "test_broken"),
        ]
    }

    cache_io = CacheIO(protostar.project_root_path)
    tests_results = cache_io.read("last_failed_tests")

    assert tests_results is not None

    assert {tuple(item) for item in tests_results["targets"]} == set(
        expected_tests_results["targets"]
    )


async def test_execute_only_passing_tests(
    protostar: ProtostarFixture,
):
    await protostar.test_cairo0(
        [
            "./tests/test_passing.cairo",
        ],
    )

    cache_io = CacheIO(protostar.project_root_path)
    tests_results = cache_io.read("last_failed_tests")

    assert tests_results is not None

    assert tests_results is None or not tests_results["targets"]
