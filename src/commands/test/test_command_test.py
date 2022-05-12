# pylint: disable=invalid-name
import re
from dataclasses import fields
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.commands.test import TestCommand


@pytest.mark.asyncio
async def test_test_command_runs_scheduler_properly(mocker: MockerFixture):
    args = TestCommand.Args(
        target=Path("foo"),
        match=re.compile("foo"),
        omit=re.compile("bar"),
        cairo_path=[Path() / "baz"],
    )
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
        match_pattern=args.match,
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


def test_arguments_match_corresponding_dataclass(mocker: MockerFixture):
    cmd_args = TestCommand(mocker.MagicMock(), mocker.MagicMock()).arguments
    cmd_args_names = [cmd_arg.name.replace("-", "_") for cmd_arg in cmd_args]
    expected_names = [field.name for field in fields(TestCommand.Args)]

    for expected_name in expected_names:
        assert expected_name in cmd_args_names
