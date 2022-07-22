import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import List

from typing_extensions import Literal

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway.starknet_interaction import StarknetInteraction
from protostar.utils.log_color_provider import LogColorProvider


class Migrator:
    Config = MigratorExecutionEnvironment.Config

    @dataclass(frozen=True)
    class Result:
        starknet_interactions: List[StarknetInteraction]

        def save_as_json(self, output_file_path: Path):
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(dataclasses.asdict(self), output_file, indent=4)

    class Factory:
        def __init__(
            self,
            migrator_execution_environment_factory: MigratorExecutionEnvironment.Factory,
        ) -> None:
            self._migrator_execution_environment_factory = (
                migrator_execution_environment_factory
            )

        def set_logger(
            self, logger: Logger, log_color_provider: LogColorProvider
        ) -> None:
            self._migrator_execution_environment_factory.set_logger(
                logger, log_color_provider
            )

        async def build(self, migration_file_path: Path, config: "Migrator.Config"):
            migrator_execution_env = (
                await self._migrator_execution_environment_factory.build(
                    migration_file_path, config=config
                )
            )

            return Migrator(migrator_execution_environment=migrator_execution_env)

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
    ) -> None:
        self._migrator_execution_environment = migrator_execution_environment

    async def run(self, mode: Literal["up", "down"]) -> Result:
        assert mode in ("up", "down")

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
        prefix = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        output_file_path = output_dir_path / f"{prefix}_{migration_basename}.json"

        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True)

        result.save_as_json(output_file_path)
