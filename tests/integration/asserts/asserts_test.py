# pylint: disable=invalid-name
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.commands.test import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_asserts(mocker: MockerFixture):
    protostar_directory_mock = mocker.MagicMock()
    cast(MagicMock, protostar_directory_mock.add_protostar_cairo_dir).return_value = [
        Path() / "cairo"
    ]

    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=protostar_directory_mock,
    ).run(TestCommand.Args(target=Path(__file__).parent / "asserts_test.cairo"))

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
