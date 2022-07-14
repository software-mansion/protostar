from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from protostar import TestCommand
from tests.integration.conftest import assert_cairo_test_cases


@pytest.mark.asyncio
async def test_basic(mocker: MockerFixture):
    protostar_directory_mock = mocker.MagicMock()
    cast(MagicMock, protostar_directory_mock.add_protostar_cairo_dir).return_value = [
        Path() / "cairo"
    ]

    testing_summary = await TestCommand(
        project=mocker.MagicMock(),
        protostar_directory=protostar_directory_mock,
    ).test(
        targets=[f"{Path(__file__).parent}/basic_test.cairo"],
        seed=10,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "test_fuzz",
        ],
        expected_failed_test_cases_names=["test_fails_if_big"],
    )
