import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway.starknet_request import StarknetRequest


class Migrator:
    Config = MigratorExecutionEnvironment.Config

    @dataclass(frozen=True)
    class History:
        starknet_requests: List[StarknetRequest]

        def save_as_json(self, output_file_path: Path):
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(dataclasses.asdict(self), output_file, indent=4)

    class Builder:
        def __init__(self) -> None:
            self._migrator_execution_environment: Optional[
                MigratorExecutionEnvironment
            ] = None

        def set_migrator_execution_environment(
            self,
            migrator_execution_environment: MigratorExecutionEnvironment,
        ) -> None:
            self._migrator_execution_environment = migrator_execution_environment

        def build(self):
            assert self._migrator_execution_environment is not None
            return Migrator(
                migrator_execution_environment=self._migrator_execution_environment
            )

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
    ) -> None:
        self._migrator_execution_environment = migrator_execution_environment

    async def run(self, rollback=False) -> History:
        await self._migrator_execution_environment.invoke(
            function_name="down" if rollback else "up"
        )

        return Migrator.History(
            # pylint: disable=line-too-long
            starknet_requests=self._migrator_execution_environment.cheatcode_factory.gateway_facade.starknet_requests
        )

    @staticmethod
    def save_history(
        history: History,
        migration_file_basename: str,
        output_dir_path: Path,
    ):
        prefix = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        output_file_path = output_dir_path / f"{prefix}_{migration_file_basename}.json"

        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True)

        history.save_as_json(output_file_path)
