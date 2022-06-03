# pylint: disable=invalid-name
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
    args.target = ["foo"]
    args.ignore = ["bar"]
    args.cairo_path = [Path() / "baz"]

    TestCollectorMock = mocker.patch(
        "protostar.commands.test.test_command.TestCollector",
    )
    TestSchedulerMock = mocker.patch(
        "protostar.commands.test.test_command.TestScheduler"
    )
    TestingLiveLogger = mocker.patch(
        "protostar.commands.test.test_command.TestingLiveLogger"
    )
    project_mock = mocker.MagicMock()
    resolve_project_root_mock = mocker.MagicMock()
    project_root = "."
    resolve_project_root_mock.return_value = project_root
    project_mock.project_root.resolve = resolve_project_root_mock

    protostar_directory_mock = mocker.MagicMock()
    protostar_directory_mock.add_protostar_cairo_dir.return_value = args.cairo_path
    test_command = TestCommand(project_mock, protostar_directory_mock)

    await test_command.run(args)

    cast(MagicMock, TestCollectorMock.return_value.collect).assert_called_once_with(
        targets=args.target,
        ignored_targets=args.ignore,
        default_test_suite_glob=project_root,
    )
    TestingLiveLogger.assert_called_once()
    cast(MagicMock, TestSchedulerMock.return_value.run).assert_called_once()
    assert (
        str(args.cairo_path[0])
        in cast(MagicMock, TestSchedulerMock.return_value.run).call_args_list[0][1][
            "include_paths"
        ]
    )
