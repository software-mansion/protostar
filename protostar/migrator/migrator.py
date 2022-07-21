from pathlib import Path

from reactivex import Subject
from typing_extensions import Literal

from protostar.migrator.migrator_cheatcodes_factory import MigratorCheatcodeFactory
from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)


class Migrator:
    Config = MigratorExecutionEnvironment.Config

    class Factory:
        def __init__(
            self,
            migrator_execution_environment_factory: MigratorExecutionEnvironment.Factory,
        ) -> None:
            self._migrator_execution_environment_factory = (
                migrator_execution_environment_factory
            )

        async def build(self, migration_file_path: Path, config: "Migrator.Config"):
            return Migrator(
                migrator_execution_environment=await self._migrator_execution_environment_factory.build(
                    migration_file_path, config=config
                )
            )

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
    ) -> None:
        self._migrator_execution_environment = migrator_execution_environment

    async def run(self, mode: Literal["up", "down"]):
        assert mode in ("up", "down")

        starknet_interactions_subject = Subject[
            MigratorCheatcodeFactory.StarknetInteraction
        ]()

        with starknet_interactions_subject:
            self._migrator_execution_environment.cheatcode_factory.starknet_interaction_subject = (
                starknet_interactions_subject
            )
            await self._migrator_execution_environment.invoke(function_name=mode)

        # TODO: save the results
