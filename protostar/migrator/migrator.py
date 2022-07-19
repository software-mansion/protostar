from pathlib import Path

from typing_extensions import Literal

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)


class Migrator:
    class Factory:
        @staticmethod
        async def build(migration_file_path: Path):
            return Migrator(
                migrator_execution_environment=await MigratorExecutionEnvironment.Factory().build(
                    migration_file_path
                )
            )

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
    ) -> None:
        self._migrator_execution_environment = migrator_execution_environment

    async def run(self, mode: Literal["up", "down"]):
        assert mode in ("up", "down")

        await self._migrator_execution_environment.invoke(function_name=mode)

        # TODO: save the results
