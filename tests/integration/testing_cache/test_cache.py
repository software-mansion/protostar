import pytest

from protostar.self.cache import CacheUtil
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture
from tests.data.tests import *


@pytest.fixture(name="protostar", scope="module")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files({"./tests/test_passing.cairo": TEST_PASSING})
        protostar.create_files(
            {"./tests/test_partially_passing.cairo": TEST_PARTIALLY_PASSING}
        )
        protostar.create_files({"./tests/test_failing.cairo": TEST_FAILING})
        protostar.build_sync()
        yield protostar


async def test_execute_all_tests(
    protostar: ProtostarFixture,
):
    try:
        await protostar.test(
            [
                "./tests/test_passing.cairo",
                "./tests/test_partially_passing.cairo",
                "./tests/test_failing.cairo",
            ]
        )
    except Exception as e:
        assert str(e) == "Not all test cases passed"

    expected_tests_results = {
        "failed_tests": [
            ("tests/test_failing.cairo", "test_fail1"),
            ("tests/test_partially_passing.cairo", "test_fail1"),
            ("tests/test_failing.cairo", "test_fail2"),
            ("tests/test_partially_passing.cairo", "test_fail2"),
        ]
    }

    cache_util = CacheUtil(str(protostar.project_root_path))
    tests_results = cache_util.obtain("test_results")

    assert tests_results is not None

    assert {tuple(item) for item in tests_results["failed_tests"]} == set(
        expected_tests_results["failed_tests"]
    )


async def test_execute_only_passing_tests(
    protostar: ProtostarFixture,
):
    await protostar.test(
        [
            "./tests/test_passing.cairo",
        ]
    )

    cache_util = CacheUtil(str(protostar.project_root_path))
    tests_results = cache_util.obtain("test_results")

    assert tests_results is not None

    assert tests_results is None or not tests_results["failed_tests"]
