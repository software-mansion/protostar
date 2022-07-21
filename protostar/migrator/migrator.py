import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from reactivex import Subject
from typing_extensions import Literal

from protostar.migrator.migrator_cheatcodes_factory import MigratorCheatcodeFactory
from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway.starknet_interaction import StarknetInteraction


class Migrator:
    Config = MigratorExecutionEnvironment.Config

    @dataclass(frozen=True)
    class Result:
        starknet_interactions: List[StarknetInteraction]

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

    async def run(self, mode: Literal["up", "down"]) -> Result:
        assert mode in ("up", "down")

        starknet_interactions_subject = Subject[
            MigratorCheatcodeFactory.StarknetInteraction
        ]()

        with starknet_interactions_subject:
            self._migrator_execution_environment.cheatcode_factory.starknet_interaction_subject = (
                starknet_interactions_subject
            )
            await self._migrator_execution_environment.invoke(function_name=mode)

        return Migrator.Result(
            # pylint: disable=line-too-long
            starknet_interactions=self._migrator_execution_environment.cheatcode_factory.gateway_facade.starknet_interactions
        )

    @staticmethod
    def save_result(
        result: Result,
        migration_file_path: Path,
        output_dir_path: Path,
    ):
        migration_basename = Path(migration_file_path).stem
        prefix = datetime.strftime(datetime.now(), "YYMMDDHHmmss")
        output_path = output_dir_path / f"{prefix}_{migration_basename}"

        if not output_path.exists():
            output_dir_path.mkdir(parents=True)

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(dataclasses.asdict(result), output_file)
