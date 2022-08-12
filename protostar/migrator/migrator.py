import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import List, Optional

from protostar.migrator.migrator_execution_environment import (
    MigratorExecutionEnvironment,
)
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.starknet_gateway.starknet_request import StarknetRequest
from protostar.utils.log_color_provider import LogColorProvider


class Migrator:
    @dataclass(frozen=True)
    class History:
        starknet_requests: List[StarknetRequest]

        def save_as_json(self, output_file_path: Path):
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(dataclasses.asdict(self), output_file, indent=4)

    class Builder:
        def __init__(
            self,
            migrator_execution_environment_builder: MigratorExecutionEnvironment.Builder,
            gateway_facade_builder: GatewayFacade.Builder,
            cwd: Optional[Path] = None,
        ) -> None:
            self._migrator_execution_environment_builder = (
                migrator_execution_environment_builder
            )
            self._gateway_facade_builder = gateway_facade_builder
            self._logger: Optional[Logger] = None
            self._log_color_provider: Optional[LogColorProvider] = None
            self._migrator_execution_environment_config = (
                MigratorExecutionEnvironment.Config()
            )
            self._cwd = cwd

        def set_logger(
            self, logger: Logger, log_color_provider: LogColorProvider
        ) -> None:
            self._logger = logger
            self._log_color_provider = log_color_provider

        def set_network(self, network: str):
            self._gateway_facade_builder.set_network(network)

        def set_migration_execution_environemnt_config(
            self, config: MigratorExecutionEnvironment.Config
        ):
            self._migrator_execution_environment_config = config

        async def build(self, migration_file_path: Path):
            gateway_facade = self._gateway_facade_builder.build()

            if self._logger:
                assert self._log_color_provider
                gateway_facade.set_logger(self._logger, self._log_color_provider)

            self._migrator_execution_environment_builder.set_gateway_facade(
                gateway_facade
            )

            migrator_execution_env = (
                await self._migrator_execution_environment_builder.build(
                    migration_file_path,
                    config=self._migrator_execution_environment_config,
                )
            )

            return Migrator(
                migrator_execution_environment=migrator_execution_env, cwd=self._cwd
            )

    def __init__(
        self,
        migrator_execution_environment: MigratorExecutionEnvironment,
        cwd: Optional[Path] = None,
    ) -> None:
        self._cwd = cwd or Path()
        self._migrator_execution_environment = migrator_execution_environment

    async def run(self, rollback=False) -> History:
        await self._migrator_execution_environment.invoke(
            function_name="down" if rollback else "up"
        )

        return Migrator.History(
            # pylint: disable=line-too-long
            starknet_requests=self._migrator_execution_environment.cheatcode_factory.gateway_facade.get_starknet_requests()
        )

    def save_history(
        self,
        history: History,
        migration_file_basename: str,
        output_dir_relative_path: Path,
    ):
        output_dir_path = self._cwd / output_dir_relative_path
        prefix = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        output_file_path = output_dir_path / f"{prefix}_{migration_file_basename}.json"

        if not output_dir_path.exists():
            output_dir_path.mkdir(
                parents=True,
            )

        history.save_as_json(output_file_path)
