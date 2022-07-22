from asyncio import Future
from pathlib import Path
from typing import cast

import pytest
from pytest_mock import MockerFixture

from protostar.commands.migrate.migrate_command import MigrateCommand
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.migrator import Migrator
from protostar.protostar_exception import ProtostarException


def mock_migrator_factory(
    mocker: MockerFixture, migrator_mock: Migrator
) -> Migrator.Factory:
    migrator_mock_future = Future()
    migrator_mock_future.set_result(migrator_mock)
    migrator_factory_mock = cast(Migrator.Factory, mocker.MagicMock())
    cast(
        mocker.MagicMock, migrator_factory_mock.build
    ).return_value = migrator_mock_future
    return migrator_factory_mock


async def test_cheatcode_exceptions_are_pretty_printed(mocker: MockerFixture):
    migrator_mock = cast(Migrator, mocker.MagicMock())
    cast(mocker.MagicMock, migrator_mock.run).side_effect = CheatcodeException(
        cheatcode_name="CHEATCODE_NAME", message="CHEATCODE_EX_MSG"
    )

    migrate_command = MigrateCommand(
        migrator_factory=mock_migrator_factory(mocker, migrator_mock),
        logger=mocker.MagicMock(),
        log_color_provider=mocker.MagicMock(),
    )

    with pytest.raises(ProtostarException, match="CHEATCODE_EX_MSG"):
        await migrate_command.migrate(
            gateway_url="http://localhost:3000/",
            network=None,
            migration_file_path=Path(),
            rollback=False,
            output_dir_path=None,
        )
