# pylint: disable=invalid-name
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.commands.test.test_command import TestCommand

CURRENT_DIR = Path(__file__).parent


@pytest.mark.asyncio
async def test_asserts(mocker: MockerFixture):
    protostar_directory_mock = mocker.MagicMock()
    cairo_dir = Path(CURRENT_DIR, "..", "..", "..", "cairo").resolve()
    cast(MagicMock, protostar_directory_mock.add_protostar_cairo_dir).return_value = [
        cairo_dir
    ]

    testing_summary = await TestCommand(
        project=mocker.MagicMock(), protostar_directory=protostar_directory_mock
    ).run(TestCommand.Args(target=CURRENT_DIR / "test_asserts.cairo"))

    assert len(testing_summary.passed) == 10
    assert len(testing_summary.failed) == 0
    assert len(testing_summary.broken) == 0
