from pathlib import Path

from typing_extensions import Literal

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)


class Migrator:
    class Factory:
        def __init__(
            self,
            migrator_execution_environment_factory: MigratorExecutionEnvironment.Factory,
        ) -> None:
            self._migrator_execution_environment_factory = (
                migrator_execution_environment_factory
            )

        async def build(self, migration_file_path: Path):
            return Migrator(
                migrator_execution_environment=await self._migrator_execution_environment_factory.build(
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
