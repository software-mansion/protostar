# pylint: disable=invalid-name
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from protostar.commands.test import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_asserts(mocker: MockerFixture):
    protostar_directory_mock = mocker.MagicMock()
    protostar_directory_mock.protostar_test_only_cairo_packages_path = Path() / "cairo"

    testing_summary = await TestCommand(
        project_root_path=Path(),
        project_cairo_path_builder=mocker.MagicMock(),
        protostar_directory=protostar_directory_mock,
    ).test(targets=[f"{Path(__file__).parent}/asserts_test.cairo"])

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_assert_eq",
            "test_assert_not_eq",
            "test_assert_signed_lt",
            "test_assert_unsigned_lt",
            "test_assert_signed_le",
            "test_assert_unsigned_le",
            "test_assert_signed_gt",
            "test_assert_unsigned_gt",
            "test_assert_signed_ge",
            "test_assert_unsigned_ge",
        ],
        expected_failed_test_cases_names=[],
    )
