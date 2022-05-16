# pylint: disable=invalid-name
import re
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from protostar.commands.test import TestCommand


@pytest.mark.asyncio
async def test_test_command_runs_scheduler_properly(mocker: MockerFixture):
    args = SimpleNamespace()
    args.target = Path("foo")
    args.omit = re.compile("bar")
    args.cairo_path = [Path() / "baz"]

    TestCollectorMock = mocker.patch(
        "src.commands.test.test_command.TestCollector",
    )
    TestSchedulerMock = mocker.patch("src.commands.test.test_command.TestScheduler")
    TestingLiveLogger = mocker.patch("src.commands.test.test_command.TestingLiveLogger")
    project_mock = mocker.MagicMock()
    protostar_directory_mock = mocker.MagicMock()
    protostar_directory_mock.add_protostar_cairo_dir.return_value = args.cairo_path
    test_command = TestCommand(project_mock, protostar_directory_mock)

    await test_command.run(args)

    cast(MagicMock, TestCollectorMock.return_value.collect).assert_called_once_with(
        target=args.target,
        omit_pattern=args.omit,
    )
    TestingLiveLogger.assert_called_once()
    cast(MagicMock, TestSchedulerMock.return_value.run).assert_called_once()
    assert (
        str(args.cairo_path[0])
        in cast(MagicMock, TestSchedulerMock.return_value.run).call_args_list[0][1][
            "include_paths"
        ]
    )
